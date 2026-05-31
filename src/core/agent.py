from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from src.config import get_settings

# Phase 7: Code Interpreter
from src.core.tools import code_interpreter

settings = get_settings()

llm = ChatGroq(
    model=settings.llm_model,
    temperature=0.7,
    groq_api_key=settings.groq_api_key
)

def agent_node(state):
    messages = state["messages"]
    question = messages[-1].content
    lower_question = question.lower()

    # Smart Decision
    is_plot_request = any(word in lower_question for word in 
                         ["plot", "graph", "chart", "draw", "visualize", "sine", "cos", "show me the curve"])

    if is_plot_request:
        # Use code interpreter for plots
        result = code_interpreter.invoke(question)
        return {"messages": messages + [AIMessage(content=result)]}
    else:
        # Normal response for calculations or general questions
        history = "\n".join([
            f"User: {m.content}" if isinstance(m, HumanMessage) else f"Assistant: {m.content}"
            for m in messages[:-1]
        ])

        prompt = f"""You are SJ, a smart and helpful AI assistant.

Previous conversation:
{history if history else "This is the first message."}

New Question: {question}

Answer directly and naturally. For math/calculations, give the final number clearly."""

        response = llm.invoke(prompt)
        return {"messages": messages + [AIMessage(content=response.content)]}


# Workflow
workflow = StateGraph(dict)
workflow.add_node("agent", agent_node)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

agent = workflow.compile()