from langchain_community.tools.tavily_search import TavilySearchResults
from src.config import get_settings

settings = get_settings()

def get_web_search_tool():
    return TavilySearchResults(
        tavily_api_key=settings.tavily_api_key,
        max_results=3,
        search_depth="advanced",
        include_answer=True
    )