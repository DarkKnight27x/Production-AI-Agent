from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from src.config import get_settings
from src.core.tools import get_web_search_tool, get_code_interpreter_tool

settings = get_settings()

llm = ChatGroq(
    model=settings.llm_model,
    temperature=0.7,
    groq_api_key=settings.groq_api_key
)

web_search = get_web_search_tool()
code_interpreter = get_code_interpreter_tool()

def agent_node(state):
    messages = state["messages"]
    question = messages[-1].content

    history = "\n".join([
        f"User: {m.content}" if isinstance(m, HumanMessage) else f"Assistant: {m.content}"
        for m in messages[:-1]
    ])

    # Tool Routing Prompt
    routing_prompt = f"""Decide what to do:

Question: {question}

Options:
1. Answer directly (general knowledge)
2. Use Web Search (latest info, news, facts)
3. Use Code Interpreter (math, calculation, plot)

Previous conversation:
{history if history else "First message."}

Reply with only the number (1, 2 or 3)."""

    decision = llm.invoke(routing_prompt).content.strip()

    if "2" in decision:
        tool_result = web_search.invoke({"query": question})
        context = f"Web Search Result: {tool_result}"
    elif "3" in decision:
        try:
            code_result = code_interpreter.run(question)
            context = f"Code Result: {code_result}"
        except:
            context = "Code execution failed."
    else:
        context = ""

    # Final Answer
    final_prompt = f"""Previous conversation:
{history if history else ""}

Additional Info: {context}

Question: {question}

Answer naturally and helpfully."""

    response = llm.invoke(final_prompt)
    
    return {"messages": messages + [AIMessage(content=response.content)]}

# Graph
workflow = StateGraph(dict)
workflow.add_node("agent", agent_node)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

agent = workflow.compile()