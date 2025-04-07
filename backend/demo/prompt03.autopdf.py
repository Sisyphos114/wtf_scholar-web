import os
import re
import requests
import json
from langchain_community.chat_models import ChatPerplexity, ChatOllama
from scidownl import scihub_download
import urllib.request

S2_API_KEY = os.getenv("S2_API_KEY")

def get_paper_title(llm, prompt, reference):
    print(reference)
    response = llm.invoke(prompt.format(reference=reference))
    for line in response.content.split('\n'):
        payload = re.match('TITLE: (.*)', line)
        if payload != None:
            return payload.group(1)
    return None

def get_semantic_scholar_paperId(title):
    response = requests.get(url="https://api.semanticscholar.org/graph/v1/paper/search",
                            headers={"X-API-KEY": S2_API_KEY},
                            params={"query":title, "limit":1})
    payload = response.json()
    if 'data' not in payload.keys():
        return None
    else:
        return payload['data'][0]['paperId']


known_bad_entries = {
    "(Sources to be added)",
}

if __name__ == "__main__":

    i_am_rich = False 
    if i_am_rich:
        model = "llama-3.1-sonar-small-128k-online"
        llm = ChatPerplexity(api_key=os.environ["PPLX_API_KEY"], temperature=0, model=model)
    else:
        model = "llama3.1"
        llm = ChatOllama(model=model)
    with open("prompt03-gettitle.txt", 'r') as f:
        prompt = f.read()
    with open("outline.txt", 'r') as f:
        outline = f.read()

    pdf_filename = './pdfs/{filename}.pdf'
    paper_type = 'title'
    with open("prompt02.out", 'r') as f:
        line = f.readline()
        found = False
        while line is not None and line != "":
            ref_reached = re.search(r'References:', line)
            if ref_reached != None:
                found = True
                break
            line = f.readline()
        if found == False:
            print('No References section found')
            exit()
        refnum2reference = dict()
        while line is not None and line != "":
            payload = re.match(r'(\d+). (.+)', line)
            if payload != None:
                refnum2reference[payload.group(1)] = payload.group(2)
            line = f.readline()

    for refnum in refnum2reference.keys():
        ref_entry = refnum2reference[refnum]
        if ref_entry.startswith('http'):
            if ref_entry.endswith('/'):
                basename = ref_entry[:-1]
            elif ref_entry.endswith('/full'):
                basename = ref_entry[:-5]
            else:
                basename = ref_entry
            basename = re.search('([^/]+)$', basename).group(1)
            filename = pdf_filename.format(filename=basename)
            print(f'Downloading {ref_entry}')
            urllib.request.urlretrieve(ref_entry, filename)
        else:
            title = get_paper_title(llm, prompt, ref_entry)
            print(f'Downloading {title}')
            paperId = get_semantic_scholar_paperId(title)
            if paperId == None:
                continue
            title = re.sub(r"[\W\d_]+$", "", title)
            filename = pdf_filename.format(filename=paperId)
            scihub_download(title, paper_type=paper_type, out=filename)


        # get paper content from scihub
    exit()



    with open("prompt02.out", 'r') as f:
        line = f.readline()
        while line is not None and line != "":
            payload = re.search(r'FACT: (.*)', line)
            if payload != None:
                fact = payload.group(1)
                refnums = re.findall(r'\[(\d{1,3})\]', fact)
                if len(refnums) != 0:
                    for refnum in refnums:
                        print(f'verifying against {refnum}. {refnum2reference[refnum]}')
                        print(get_paper_id(refnum2reference[refnum]))
                else:

                    for refnum in refnum2reference.keys():
                        content = refnum2reference[refnum]
                        # check if fact is from content 


            line = f.readline()

