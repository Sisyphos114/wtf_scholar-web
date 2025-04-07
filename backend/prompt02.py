from langchain_community.chat_models import ChatPerplexity, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.embeddings.gpt4all import GPT4AllEmbeddings
import re
import os
from utils import get_citenum
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') 
if __name__ == "__main__":

    use_pplx = True 
    vectorstore_dir = "./vectorstore"
    if use_pplx:
        model = "llama-3.1-sonar-large-128k-online"
        llm = ChatPerplexity(api_key=os.environ["PPLX_API_KEY"], temperature=0, model=model)
    else:
        model = "llama3.1"
        base_llm = ChatOllama(model=model)
        embedding = GPT4AllEmbeddings(model_name="all-MiniLM-L6-v2.gguf2.f16.gguf",
                                      gpt4all_kwargs={'allow_download': 'True'})
        vectorstore = Chroma(persist_directory=vectorstore_dir, embedding_function=embedding)
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
        llm = RetrievalQA.from_chain_type(
                  llm=base_llm,
                  chain_type="stuff",
                  retriever=vectorstore.as_retriever()
              )

    with open("outline.txt", 'r') as f:
        outline = f.read()
        outlines = outline.split('\n')
        article_title = outlines[0]
    
    with open("prompt02-area2fact.txt", 'r') as f:
        prompt = f.read()

    collected = []
    section_title = None
    with open("prompt01.out", 'r') as f:
        line = f.readline()
        while line is not None and line != "":
            if re.match('.*ection [\\d\\.]*', line) != None:
                if section_title != None:
                    collected.append((section_title, section_areas))
                section_title = line
                section_areas = []
            if re.match(r'^\s*\d+\. .*', line) != None: 
                section_areas.append(line)
            line = f.readline()
        collected.append((section_title, section_areas))

    citations = dict()
    for section_title, section_areas in collected:
        print()
        print(section_title)
        for i, area in enumerate(section_areas):
            print(area)
            response = llm.invoke(prompt.format(article_title=article_title,
                                                section_title=section_title,
                                                area=area))
            llm_output = response['result'] if type(response)==dict else response.content
            references_reached = False
            facts = []
            citenum_map = dict()
            inline_citenums = []
            for line in llm_output.split('\n'):
                if not references_reached and re.match('^FACT.*', line) != None: 
                    facts.append(line)
                    inline_citenums.extend( re.findall(r'\[(\d+)\]', line) )
                elif re.match('^References', line) != None:
                    references_reached = True
                elif references_reached:
                    if re.match(r'^\d+\. ', line) != None: 
                        ref_entry = re.match(r'^(\d+)\. (.*)', line)
                        reference = ref_entry.group(2)
                        citenum = get_citenum(citations, llm, reference)
                        citenum_map[ref_entry.group(1)] = citenum
            #print(citenum_map)
            for fact in facts:
                 replaced = False
                 for i in inline_citenums:
                     if re.search(f'[{i}]', fact) != None:
                         if i in citenum_map.keys():
                             if citenum_map[i] != 0:
                                 fact = fact.replace(f'[{i}]', f'<___{citenum_map[i]}___>')
                             else:
                                 fact = fact.replace(f'[{i}]', '')
                         else:
                             fact = fact.replace(f'[{i}]', '')
                 fact = fact.replace('<___', '[')
                 fact = fact.replace('___>', ']')
                 print(fact)
                 print()
            print()
    if len(citations) != 0:
        print("References:")
    for i in citations.keys():
        reference, _, _ = citations[i]
        print(f"{i}. {reference}")
        print()

