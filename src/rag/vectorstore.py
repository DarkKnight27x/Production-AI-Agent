from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import get_settings
import os

settings = get_settings()

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)

def create_vectorstore(docs):
    """Create FAISS vector store from documents"""
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore

def save_vectorstore(vectorstore):
    """Save FAISS index"""
    vectorstore.save_local(settings.vector_db_path)

def load_vectorstore():
    """Load existing FAISS index"""
    embeddings = get_embeddings()
    if os.path.exists(settings.vector_db_path):
        return FAISS.load_local(settings.vector_db_path, embeddings, allow_dangerous_deserialization=True)
    return None