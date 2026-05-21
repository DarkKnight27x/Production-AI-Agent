from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from src.config import get_settings
from src.rag.retriever import get_retriever

settings = get_settings()

llm = ChatGroq(
    model=settings.llm_model,
    temperature=0.7,
    groq_api_key=settings.groq_api_key
)

def build_history(messages):
    parts = []
    for m in messages[:-1]:
        if isinstance(m, HumanMessage):
            parts.append(f"User: {m.content}")
        elif isinstance(m, AIMessage):
            parts.append(f"Assistant: {m.content}")
    return "\n".join(parts)


# ── 1. Classifier (NO LLM — pure logic) ──────────────────────────────────────
FOLLOWUP_PRONOUNS = ["his", "her", "their", "he", "she", "they", "them", "it", "its", "that", "this", "those", "these"]
DOC_KEYWORDS = ["document", "pdf", "file", "uploaded", "according to", "in the document", "the text", "syllabus", "report", "paper"]

def classifier_node(state):
    messages = state["messages"]
    question = messages[-1].content.lower().strip()
    has_history = len(messages) > 1

    # If there's conversation history AND question starts with a pronoun/follow-up word → CHAT
    words = question.split()
    starts_with_pronoun = words[0] in FOLLOWUP_PRONOUNS if words else False
    contains_pronoun = any(w in FOLLOWUP_PRONOUNS for w in words)
    contains_doc_keyword = any(kw in question for kw in DOC_KEYWORDS)

    if contains_doc_keyword:
        route = "rag"
    elif has_history and (starts_with_pronoun or contains_pronoun):
        route = "chat"
    elif not has_history:
        route = "chat"  # first message with no docs mentioned → chat
    else:
        route = "chat"  # default to chat, only RAG when explicitly about docs

    return {**state, "route": route}


# ── 2. Router ─────────────────────────────────────────────────────────────────
def route_decision(state):
    return state.get("route", "chat")


# ── 3. Chat node ──────────────────────────────────────────────────────────────
def chat_node(state):
    messages = state["messages"]
    question = messages[-1].content
    history = build_history(messages)

    if history:
        prompt = f"""You are a helpful assistant with full memory of this conversation.

Previous conversation:
{history}

New question: {question}

RULES:
- The conversation history above is your memory. Use it to resolve any pronouns like "he", "she", "his", "they".
- If someone was mentioned earlier, you know who they are. Answer directly.
- Never mention documents, PDFs, context, or system internals.
- Answer naturally as if you remember everything said above.

Answer:"""
    else:
        prompt = f"""You are a helpful assistant.

Question: {question}

Answer directly and naturally.

Answer:"""

    response = llm.invoke(prompt)
    return {"messages": messages + [AIMessage(content=response.content)]}


# ── 4. RAG node ───────────────────────────────────────────────────────────────
def rag_node(state):
    messages = state["messages"]
    question = messages[-1].content
    history = build_history(messages)

    retriever = get_retriever()
    if retriever is None:
        return {"messages": messages + [AIMessage(content="No documents ingested yet. Please upload and ingest documents first.")]}

    retrieved_docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = f"""You are a helpful assistant. Use the document context below to answer.

Previous conversation:
{history if history else "None"}

Context from documents:
{context}

Question: {question}

Answer based on the context. If the answer isn't in the context, say so.

Answer:"""

    response = llm.invoke(prompt)
    return {"messages": messages + [AIMessage(content=response.content)]}


# ── 5. Graph ──────────────────────────────────────────────────────────────────
workflow = StateGraph(dict)

workflow.add_node("classifier", classifier_node)
workflow.add_node("chat", chat_node)
workflow.add_node("rag", rag_node)

workflow.add_edge(START, "classifier")
workflow.add_conditional_edges(
    "classifier",
    route_decision,
    {"chat": "chat", "rag": "rag"}
)
workflow.add_edge("chat", END)
workflow.add_edge("rag", END)

agent = workflow.compile()