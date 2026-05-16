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

def researcher_node(state):
    question = state["messages"][-1].content
    print(f"🔍 Researcher working on: {question}")
    
    # Check documents
    retriever = get_retriever(k=6)
    context = ""
    if retriever:
        docs = retriever.invoke(question)
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs])
    
    # If no relevant documents, use web search
    if not context or len(context) < 100:
        print("🌐 No relevant documents → Using Web Search")
        search_result = web_search.invoke({"query": question})
        context = f"Web Search Result:\n{search_result}"
    
    return {"context": context, "messages": state["messages"]}

def critic_node(state):
    question = state["messages"][-1].content
    context = state.get("context", "")
    
    critique_prompt = f"""Review this information for the question and give honest feedback:

Question: {question}
Information: {context}

Critique:"""

    critique = llm.invoke(critique_prompt).content
    return {"context": context, "critique": critique, "messages": state["messages"]}

def summarizer_node(state):
    question = state["messages"][-1].content
    context = state.get("context", "")
    critique = state.get("critique", "")
    
    final_prompt = f"""Answer the question clearly and naturally using the available information and critique.

Question: {question}
Available Information: {context}
Critique: {critique}

Final Answer:"""

    final_answer = llm.invoke(final_prompt).content
    print("✅ Multi-Agent completed")
    
    return {"messages": state["messages"] + [AIMessage(content=final_answer)]}

# Multi-Agent Workflow
workflow = StateGraph(dict)
workflow.add_node("researcher", researcher_node)
workflow.add_node("critic", critic_node)
workflow.add_node("summarizer", summarizer_node)

workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "critic")
workflow.add_edge("critic", "summarizer")
workflow.add_edge("summarizer", END)

agent = workflow.compile()