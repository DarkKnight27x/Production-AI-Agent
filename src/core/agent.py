from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from src.config import get_settings
from src.rag.retriever import get_retriever
from src.core.tools import get_web_search_tool

settings = get_settings()

llm = ChatGroq(
    model=settings.llm_model,
    temperature=0.6,
    groq_api_key=settings.groq_api_key
)

web_search = get_web_search_tool()

def retrieve(state):
    question = state["messages"][-1].content
    print(f"🔍 Retrieving for: {question}")
    
    retriever = get_retriever(k=6)
    context = ""
    if retriever:
        docs = retriever.invoke(question)
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs])
            print(f"✅ Retrieved {len(docs)} chunks")
    
    return {"context": context, "messages": state["messages"]}

def generate(state):
    question = state["messages"][-1].content
    context = state.get("context", "")
    
    # Step 1: Generate Initial Answer
    if context:
        initial_prompt = f"""Use the context if relevant. Be accurate.

Context:
{context}

Question: {question}

Answer:"""
    else:
        initial_prompt = question

    initial_response = llm.invoke(initial_prompt)
    initial_answer = initial_response.content

    # Step 2: Self-Critique
    critique_prompt = f"""Critique the following answer strictly for accuracy, hallucinations, completeness, and clarity.

Question: {question}
Answer: {initial_answer}

Critique:"""

    critique = llm.invoke(critique_prompt).content

    # Step 3: Generate Improved Final Answer
    final_prompt = f"""Improve the answer based on this critique. Make it more accurate and natural.

Original Answer: {initial_answer}

Critique: {critique}

Final Improved Answer:"""

    final_response = llm.invoke(final_prompt).content

    print("✅ Self-critique completed")
    return {"messages": state["messages"] + [AIMessage(content=final_response)]}

# Build the Graph
workflow = StateGraph(dict)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

agent = workflow.compile()