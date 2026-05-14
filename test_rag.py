from src.rag.retriever import load_and_process_documents 
from src.rag.vectorstore import create_vectorstore, save_vectorstore 
 
print('Loading documents...') 
docs = load_and_process_documents() 
print(f'Created {len(docs)} chunks') 
 
print('Creating vectorstore...') 
vectorstore = create_vectorstore(docs) 
save_vectorstore(vectorstore) 
print('Vectorstore saved successfully!') 
