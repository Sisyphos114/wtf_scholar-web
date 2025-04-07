# Does PPLX allow tool yet?
from langchain import hub
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_models import ChatPerplexity
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import Tool

persist_directory = "./vectorstore"
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
retriever = vectorstore.as_retriever()
local_tool = Tool(
    name="VectorStore",
    func=retriever.get_relevant_documents,
    description="Useful for retrieving relevant information from the vectorstore"
)

instructions = """You are an assistant."""
base_prompt = hub.pull("langchain-ai/openai-functions-template")
prompt = base_prompt.partial(instructions=instructions)
llm = ChatPerplexity(model="llama-3-sonar-large-32k-chat", temperature=0)
external_tool = TavilySearchResults()

tools = [external_tool]
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor( agent=agent, tools=tools, verbose=True )

results = agent_executor.invoke({"input":
    "You are an expert in mRNA vaccines and African Swine Fever.\n"
    "Explain what the ASFV-SY18-∆CD2v/UK is and how it is relevant to the African Swine Fever"
    "Answer using only information from the tool."
    "Please show the source of your answer."
#    "You will be given a template of an article on the topic.\n"
#    "Your job is to write a few paragraphs to fill in the part marked with FIXME\n"
#    "To do so, first retrieve a few relevant articles.\n"
#    "Then, write your paragraphs based on the articles retreived."
#    "TEMPLATE:```"
#    "Section 1: mRNA Vaccines: a new hope for preventing and controlling African Swine Fever.\n"
#    "Sub-section 1.1: Live-attenuated ASFV vaccines.\n"
#    "Sub-section 1.2: Inactivated and protein ASFV vaccines.\n"
#    "Sub-section 1.3: DNA and virus-vectored ASFV vaccines.\n"
#    "Sub-section 1.4: RNA ASFV vaccines.\n"
#    "Sub-section 1.5: The challenges of developing ASFV vaccines.\n"
#    "Section 2: Key advantages of ASFV mRNA vaccines\n"
#    "Sub-section 2.1: mRNA vaccine can induce powerful Th1-bias immune response and memory\n"
#    "Sub-section 2.2: mRNA vaccine enables the development of multivalent ASFV vaccines\n"
#    "Sub-section 2.3: Flexible utility and alternation of ASFV antigens\n"
#    "Sub-section 2.4: Short development cycle, fast to manufacture, and reduces cost\n"
#    "Section 3: How to design effective ASFV mRNA vaccines\n"
#    "```"
    })
print(results['output'])
