from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from src.config import get_settings

settings = get_settings()

llm = ChatGroq(
    model=settings.llm_model,
    temperature=0.7,
    groq_api_key=settings.groq_api_key
)

def agent_node(state):
    messages = state["messages"]
    question = messages[-1].content

    history = "\n".join([
        f"User: {m.content}" if isinstance(m, HumanMessage) else f"Assistant: {m.content}"
        for m in messages[:-1]
    ])

    prompt = f"""You are SJ, a smart and helpful AI assistant.

Previous conversation:
{history if history else "This is the first message."}

New Question: {question}

Answer naturally and directly like ChatGPT.
Remember previous messages for follow-up questions.
Never mention documents, PDFs, context or uploaded files.
Just give a confident, normal answer."""

    response = llm.invoke(prompt)
    
    return {"messages": messages + [AIMessage(content=response.content)]}

workflow = StateGraph(dict)
workflow.add_node("agent", agent_node)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

agent = workflow.compile()