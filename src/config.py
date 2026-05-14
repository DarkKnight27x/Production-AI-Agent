from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key: str = ""
    openrouter_api_key: str = ""
    tavily_api_key: str = ""
    
    llm_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "all-MiniLM-L6-v2"
    temperature: float = 0.7
    
    vector_db_path: str = "faiss_index"
    
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()