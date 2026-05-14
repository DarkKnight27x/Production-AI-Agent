from langchain_core.retrievers import BaseRetriever
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.rag.vectorstore import create_vectorstore, load_vectorstore, save_vectorstore

def load_and_process_documents(data_dir="data"):
    """Load PDFs and split them"""
    loader = PyPDFDirectoryLoader(data_dir)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    return splits

def get_retriever(k=4):
    """Return retriever"""
    vectorstore = load_vectorstore()
    if vectorstore is None:
        print("No vectorstore found. Please ingest documents first.")
        return None
    return vectorstore.as_retriever(search_kwargs={"k": k})