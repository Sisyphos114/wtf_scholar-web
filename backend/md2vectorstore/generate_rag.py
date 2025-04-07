# Main vectorstore test script: generates simple article using vectorstore. also supports interactive use

# packages for vectorstore
import pysqlite3
#import sys
#sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.gpt4all import GPT4AllEmbeddings

# packages for LLM and chain
from langchain_community.chat_models import ChatPerplexity, ChatOllama
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever

# packages for prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


def get_vectorstore():
    persist_directory = "./vectorstore"
    embedding = GPT4AllEmbeddings(model_name="all-MiniLM-L6-v2.gguf2.f16.gguf",
                    gpt4all_kwargs={'allow_download': 'True'})
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    return vectorstore


def get_llm(vectorstore):
    llm = ChatPerplexity(temperature=0, model="llama-3.1-sonar-small-128k-online")
    #llm = ChatOllama(model="llama3")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 15})
    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        #("user", "Given the above conversation, generate a search query to look up."),
    ])
    history_aware_retriever = create_history_aware_retriever(
        llm = llm,
        retriever = retriever,
        prompt = retriever_prompt
    )
    retrieval_chain = create_retrieval_chain( history_aware_retriever, chain )
    return retrieval_chain


def llm_response(chain, question, chat_history):
    response = chain.invoke({
        "chat_history": chat_history,
        "input": question,
    })
    return response["answer"]


if __name__ == "__main__":
    vectorstore = get_vectorstore()
    chain = get_llm(vectorstore)

    interactive = True
    if interactive:
        chat_history = []
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break
            response = llm_response(chain, user_input, chat_history)
            chat_history.append(HumanMessage(content=user_input))
            chat_history.append(AIMessage(content=response))
            print("Assistant:", response)   
            print()
        exit()

    user_input = "Generate an article on mRNA vaccines and African Swine Fever"
    response = llm_response(chain, user_input, [])
    print(response)

