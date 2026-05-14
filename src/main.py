from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from src.config import get_settings
from src.core.agent import agent
from src.rag.retriever import load_and_process_documents
from src.rag.vectorstore import create_vectorstore, save_vectorstore

settings = get_settings()

class ChatRequest(BaseModel):
    question: str

app = FastAPI(title="Production AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "✅ Backend is running!"}

@app.post("/ingest")
async def ingest_documents():
    docs = load_and_process_documents()
    vectorstore = create_vectorstore(docs)
    save_vectorstore(vectorstore)
    return {"status": "success", "chunks": len(docs)}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        inputs = {"messages": [HumanMessage(content=request.question)]}
        result = agent.invoke(inputs)
        return {
            "question": request.question,
            "answer": result["messages"][-1].content
        }
    except Exception as e:
        return {"question": request.question, "answer": f"Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)