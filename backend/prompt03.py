from langchain_community.chat_models import ChatPerplexity, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.gpt4all import GPT4AllEmbeddings
import re
import os
from utils import get_citenum
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') 
def get_retriever(vectorstore_dir):
    embedding = GPT4AllEmbeddings(model_name="all-MiniLM-L6-v2.gguf2.f16.gguf",
                                  gpt4all_kwargs={'allow_download': 'True'})
    vectorstore = Chroma(persist_directory=vectorstore_dir, embedding_function=embedding)
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})


if __name__ == "__main__":

    retriever = get_retriever('./vectorstore')    # Get references for fact
    llm = ChatOllama(model='llama3.1')            # Rate the references
    explain_f = open('prompt03explain.out', 'w')  # Store the ratings
    with open("md2biblio.txt", 'r') as f:         # Map filenames from vectorstore to reference 
        content = f.read()
        md2biblio = dict()
        for line in content.split('\n'):
            if re.match(r'(\d+) (.*)', line) == None:
                continue
            entry = re.match(r'(\d+) (.*)', line)
            i = entry.group(1)
            reference = entry.group(2)
            md2biblio[f'md/{i}.md'] = reference

    with open("prompt03-fact2ref.txt", 'r') as f:
        prompt = f.read()

    citations = dict()
    with open("prompt02.out", 'r') as f:
        line = f.readline()
        while line is not None and line != "":

            if re.search('Subsection', line) != None:
                print(line)
                print()
                explain_f.write(f'{line}\n')

            elif re.match(r'^\d+\.', line) != None:
                print(line)
                print()
                explain_f.write(f'{line}\n')

            elif re.match('^FACT:', line) != None:
                fact = re.match('^FACT: (.*)', line).group(1)
                docs = retriever.invoke(fact)
                # attribute rating to retrieved documents
                vecdocuments = []
                veccontents = []
                ratings = []
                rationales = []
                for i, doc in enumerate(docs):
                    vecdocuments.append(doc.metadata['source'])
                    veccontents.append(doc.page_content)
                    evaluation = llm.invoke(prompt.format(fact=fact, text=doc.page_content))
                    for l in evaluation.content.split('\n'):
                        if re.search('RATING:', l) != None:
                            rating = re.search(r'RATING: (\d+)', l).group(1)
                            if rating.endswith('**'):
                                rating = rating[:-2]
                            ratings.append(int(rating))
                        elif re.search('REASON:', l) != None:
                            rationale = re.search('REASON:(.*)', l).group(1)
                            rationales.append(rationale)
                # find highest scoring document, prioritized by their retrieval order
                score = max(ratings)
                if score >= 8: # only accept document with sufficiently high score
                    i = ratings.index(score)
                    reference = md2biblio[vecdocuments[i]]
                    rationale = rationales[i]
                    content = veccontents[i]
                    citenum = get_citenum(citations, llm, reference)
                    if citenum != 0:
                        fact = f'{fact} [{citenum}]'
                    explain_f.write(f'FACT: {fact}\nSUPPORT: {content}\n')
                    explain_f.write(f'SOURCE: {reference}\nSCORE: {score}\nREASON: {rationale}\n\n')
                else:
                    explain_f.write(f'FACT: {fact}\n')
                    explain_f.write('REASON: No supporting reference\n\n')
                print('FACT:', fact)
                print()

            elif re.match('^References', line) != None:
                break

            line = f.readline()

    if len(citations) != 0:
        print("References:")
    for i in citations.keys():
        reference, _, _ = citations[i]
        print(f"{i}. {reference}")
        print()

