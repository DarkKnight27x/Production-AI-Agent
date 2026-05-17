from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from src.config import get_settings
from src.rag.retriever import get_retriever
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
    question = messages[-1].content.lower()
    
    print(f"🤖 Processing: {question}")
    
    # Check if user wants code execution / plotting / math
    code_keywords = ["plot", "calculate", "solve", "graph", "math", "code", "function", "equation"]
    needs_code = any(word in question for word in code_keywords)
    
    context = ""
    retriever = get_retriever(k=5)
    if retriever:
        docs = retriever.invoke(question)
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs])

    if needs_code:
        # Generate proper Python code first
        code_prompt = f"""Write clean, correct Python code to answer this request. Use matplotlib for plots.

Request: {messages[-1].content}

Return only the code (no explanation). Include plt.show() for plots."""

        code = llm.invoke(code_prompt).content.strip()
        print(f"Generated Code:\n{code}")
        
        try:
            result = code_interpreter.run(code)
            final_answer = f"**Code executed successfully.**\n\n{result}"
        except Exception as e:
            final_answer = f"**Code execution failed.**\n\nError: {str(e)}\n\nI tried to run this code:\n```python\n{code}\n```"
    else:
        # Normal RAG + Web Search flow
        if context:
            prompt = f"Context:\n{context}\n\nQuestion: {messages[-1].content}\nAnswer naturally."
        else:
            prompt = messages[-1].content
            
        response = llm.invoke(prompt)
        final_answer = response.content

    return {"messages": messages + [AIMessage(content=final_answer)]}

# Graph
workflow = StateGraph(dict)
workflow.add_node("agent", agent_node)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

agent = workflow.compile()