# Same as geturls_from_title.py. DOESN'T WORK
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_models import ChatPerplexity
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import PDFMinerLoader
from langchain.agents import AgentType, initialize_agent, load_tools
from pdfminer.layout import LAParams
from langchain_community.tools import DuckDuckGoSearchRun
import os
import re
from unidecode import unidecode
import time

# load paper names
#with open('references.txt', 'rb') as file:
with open('in', 'rb') as file:
    content = file.read()
content = content.decode('ascii', errors='ignore').split('\n')

instructions = """You are an assistant."""
base_prompt = hub.pull("langchain-ai/openai-functions-template")
prompt = base_prompt.partial(instructions=instructions)
llm = ChatPerplexity(model="llama-3-sonar-large-32k-chat", temperature=0)
llmx = ChatPerplexity(model="llama-3-sonar-large-32k-chat", temperature=0)
tools = load_tools(["google-serper"], llm=llm)
toolsx = [DuckDuckGoSearchRun(), TavilySearchResults()]
agent = create_openai_functions_agent(llm, tools, prompt)
agentx = create_openai_functions_agent(llmx, toolsx, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agentx_executor = AgentExecutor(agent=agentx, tools=tools, verbose=True)

url_pattern = "https?:\\/\\/[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"

# if doi is included, just extract, else get the doi from name
for num, line in enumerate(content, start=1):
    doi = re.findall(r'doi: \b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b', str(line), re.IGNORECASE)
    if line == '':
        break
    if len(doi) != 0:
        print(num, doi[0])
    else:
        results = agent_executor.invoke({"input":
            "You are a very careful assistant\n"
            "You will be given a bibliography entry.\n"
            "Your job is to search on PubMed for links to papers that may correspond to the bibliography entry\n"
            f'BIBLIOGRAPHY ENTRY:```{line}```'
            })
        urls = re.findall(url_pattern, results['output'], re.IGNORECASE)
        if len(urls) == 0:
            print(num, '[AI] not found')
        else:
            for url in urls:
                verification = agentx_executor.invoke({"input":
                    "You are a very careful assistant\n"
                    "Show me the title of the paper for the following URL.\n"
                    f'URL ENTRY:```{url}```'
                    })
                print(num, '[AI]', url)
        time.sleep(5)

