# Find the URL for each literature entry in biblio.txt, save URLs to odois.txt, otitle.txt, etc
import os
import re
from unidecode import unidecode
import requests
import json
import editdistance

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_models import ChatPerplexity
from langchain_community.tools.tavily_search import TavilySearchResults
import time

llm = ChatPerplexity(model="llama-3-sonar-large-32k-chat", temperature=0)

def search(query):
    api_key = '99be81937a83fff4762941a8bb468f45c4a0c0ca'
    url = "https://google.serper.dev/search"
    params = { "engine": "google", "q": query, "api_key": api_key }
    response = requests.get(url, params=params)
    return response

with open('biblio.txt', 'rb') as file:
    content = file.read()
content = content.decode('ascii', errors='ignore').split('\n')

doi_pattern = r'doi: \b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b'
url_pattern = "https?:\\/\\/[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"
avail_pattern = "Available from: (.*)\."

fdois   = open(  "odois.txt", "w") # scihub
ftitle  = open( "otitle.txt", "w") # scihub
fpmc    = open(  "opmid.txt", "w") # use getpubmed.sh
fdirect = open("odirect.txt", "w") # PDF or HTM -> use wget
flink   = open(  "olink.txt", "w") # unknown -> handle manually

# if doi is included, just extract, else search online
for num, line in enumerate(content, start=1):
    if line == '':
        break

    print("processing", num)
    # Handle DOIs
    doi = re.findall(doi_pattern, str(line), re.IGNORECASE)
    if len(doi) != 0:
        fdois.write(f'{num} {doi[0]}\n')
        continue

    # Handle "Available from:"
    avail = re.findall(avail_pattern, str(line), re.IGNORECASE)
    if len(avail) != 0:
        avail = avail[0].replace(' ', '')
        if re.match('.*\.pdf.*', avail):
            fdirect.write(f'{num} {avail}\n')
        elif re.match('.*doi/full/.*', avail):
            doi = re.findall('.*doi/full/(.*)', str(line), re.IGNORECASE)
            fdois.write(f'{num} {doi[0]}\n')
        elif re.match('.*htm.*', avail):
            fdirect.write(f'{num} {avail}\n')
        elif re.match('.*pmc.*', avail) or re.match('.*pubmed.*', avail):
            pmc = avail.replace('/pmc/articles/', '')
            pmc = pmc.replace('PMC', '')
            pmc = pmc.replace('https://pubmed.ncbi.nlm.nih.gov/', '')
            pmc = pmc.replace('/', '')
            fpmc.write(f'{num} {pmc}\n')
        else:
            flink.write(f'{num} {avail}\n')
        continue

    # If none of the above, then search google
    response = search(line)
    if response.status_code == 200:
        results = json.loads(response.text)
        for title, link in [(result['title'], result['link']) for result in results['organic'][:3]]:
            length = len(title)
            mindiff = 1000
            for start in range(len(line)-len(title)):
                subtitle = line[start:start+length]
                diff = editdistance.eval(title.lower(), subtitle.lower())
                if diff < mindiff:
                    mindiff = diff
            if mindiff > 12:
                break
            # title seems legit
            if re.match('.*\.pdf.*', link):
                fdirect.write(f'{num} {link}\n')
            elif re.match('.*doi/full/.*', link):
                doi = re.findall('.*doi/full/(.*)', str(link), re.IGNORECASE)
                fdois.write(f'{num} {doi[0]}\n')
            elif re.match('.*pubmed.*', link):
                pmc = link.replace('https://pubmed.ncbi.nlm.nih.gov/', '')
                pmc = pmc.replace('/', '')
                fpmc.write(f'{num} {pmc}\n')
            else: # get the full title from bibliography line using LLM
                output = llm.invoke('what is the title of the paper in this bibliography'
                      f'entry: \"{line}\". State only the title without any extra text.')
                ftitle.write(f'{num} {output.content}\n')
                time.sleep(3)
    else:
        print(f'{num} error')
