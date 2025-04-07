# Uses LLM to resolve a title to URL - DOESN'T WORK
import re
from langchain import hub
from unidecode import unidecode
import requests
import json
import editdistance
from bs4 import BeautifulSoup

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_models import ChatPerplexity
from langchain_community.document_loaders import AsyncChromiumLoader, WebBaseLoader, AsyncHtmlLoader
from googlesearch import search
import time

instructions = """You are an assistant."""
base_prompt = hub.pull("langchain-ai/openai-functions-template")
prompt = base_prompt.partial(instructions=instructions)
llm = ChatPerplexity(model="llama-3-sonar-large-32k-chat", temperature=0)

#def search(query):
    #api_key = '99be81937a83fff4762941a8bb468f45c4a0c0ca'
    #url = "https://google.serper.dev/search"
    #params = { "engine": "google", "q": query, "api_key": api_key }
#    url = "http://api.duckduckgo.com/?q=x&format=json"
#    params = { "engine": "duckduckgo", "q": query }
#    response = requests.get(url, params=params)
#    return response

with open('missing', 'rb') as file:
    content = file.read()
content = content.decode('ascii', errors='ignore').split('\n')[:-1]
content = [re.findall('^([0-9]+) (.*)$', c)[0] for c in content]

for num, title in content:

    print("processing", num)
    for link in search(title, num_results=1):
        print("retrieved link:", link)
        loader = AsyncHtmlLoader([link])
        html = loader.load()[0].page_content
        soup = BeautifulSoup(html, 'html.parser')
        #for data in soup(['style']):
        #    data.decompose()
        #html = ' '.join(soup.stripped_strings)
        print(soup)
        exit()
        #links = soup.find_all('a')
        #for link in links:
        #    print(link.get('href'))
        #print('-----------------------------------------------------------------')
        agent = create_openai_functions_agent(llm, tools=[], prompt=prompt)
        agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
        results = agent_executor.invoke({"input":
            "You are an expert in HTML\n"
            "Identify in the HTML content below for a possible URL to a PDF document.\n"
            f'HTML Content: ```{html}```'
        })
