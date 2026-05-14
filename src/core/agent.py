from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from src.config import get_settings
from src.rag.retriever import get_retriever
from src.core.tools import get_web_search_tool

settings = get_settings()

llm = ChatGroq(
    model=settings.llm_model,
    temperature=0.7,
    groq_api_key=settings.groq_api_key
)

web_search = get_web_search_tool()

def agent_node(state):
    messages = state["messages"]
    question = messages[-1].content
    
    print(f"🤖 Processing: {question}")
    
    # Try to get context from documents
    retriever = get_retriever(k=5)
    context = ""
    if retriever:
        docs = retriever.invoke(question)
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs])

    # Create prompt with memory + context
    if context:
        prompt = f"""You are a helpful AI assistant. Use the following context if relevant.

Context from documents:
{context}

Previous conversation:
{'' if len(messages) <= 1 else str(messages[:-1])}

Current Question: {question}

Answer naturally and conversationally:"""
    else:
        prompt = f"""You are a helpful AI assistant. Remember the conversation history.

Previous conversation:
{'' if len(messages) <= 1 else str(messages[:-1])}

Current Question: {question}

Answer naturally:"""

    # Bind tool
    llm_with_tools = llm.bind_tools([web_search])
    response = llm_with_tools.invoke(prompt)

    # Handle tool call (web search)
    if response.tool_calls:
        tool_result = web_search.invoke(response.tool_calls[0]['args'])
        final_prompt = f"Question: {question}\n\nWeb Search Result: {tool_result}\n\nGive a natural, updated answer."
        final_response = llm.invoke(final_prompt)
        return {"messages": messages + [AIMessage(content=final_response.content)]}

    return {"messages": messages + [AIMessage(content=response.content)]}

# Build Graph with Memory
workflow = StateGraph(dict)
workflow.add_node("agent", agent_node)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

agent = workflow.compile()