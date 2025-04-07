# Embed text documents in md/ into vectorstore
import os
import pysqlite3
import sys
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.gpt4all import GPT4AllEmbeddings
#from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = []
dirname = 'md'
for filename in os.listdir(dirname):
    filepath = os.path.join(dirname, filename)
    loader = TextLoader(filepath) 
    docs.extend(loader.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

#embedding = OpenAIEmbeddings()
embedding = GPT4AllEmbeddings(model_name="all-MiniLM-L6-v2.gguf2.f16.gguf",
                              gpt4all_kwargs={'allow_download': 'True'})

vectorstore = Chroma.from_documents(documents=splits,
                              persist_directory='./vectorstore',
                              embedding=embedding)

