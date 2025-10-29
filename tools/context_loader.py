# tools/context_loader.py
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
import os
from dotenv import load_dotenv


def load_contexts(path: str = "./context", vs_path: str = "./vectorstore/faiss"):
    load_dotenv()
    loader = DirectoryLoader(path, glob="**/*.md", loader_cls=TextLoader, show_progress=True)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)
    retriever = BM25Retriever.from_documents(split_docs)
    retriever.k = 3
    return retriever
