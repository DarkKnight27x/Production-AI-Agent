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
    print(f"🔍 Retrieving context for: {question}")
    
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
    
    # Step 1: Generate initial answer
    if context:
        initial_prompt = f"""Use the context if relevant. Answer naturally.

Context:
{context}

Question: {question}"""
    else:
        initial_prompt = question

    initial_response = llm.invoke(initial_prompt)
    initial_answer = initial_response.content

    # Step 2: Self-Critique
    critique_prompt = f"""Critique this answer strictly:
- Is it factually correct?
- Does it hallucinate?
- Is it complete and relevant?
- Any improvements needed?

Question: {question}
Answer: {initial_answer}

Critique:"""

    critique = llm.invoke(critique_prompt).content

    # Step 3: Generate final improved answer
    final_prompt = f"""Improve the answer based on the critique.

Original Answer: {initial_answer}

Critique: {critique}

Final Answer:"""

    final_response = llm.invoke(final_prompt).content

    print("✅ Self-critique & improvement done")
    return {"messages": state["messages"] + [AIMessage(content=final_response)]}

# Build Graph
workflow = StateGraph(dict)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

agent = workflow.compile()