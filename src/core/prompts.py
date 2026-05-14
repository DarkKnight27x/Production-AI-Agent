from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# System prompt for the agent
AGENT_SYSTEM_PROMPT = """You are an intelligent research assistant. 
Your goal is to provide accurate, well-reasoned answers using the provided context and tools.
Always think step-by-step. If unsure, say so clearly."""

# RAG Prompt
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Answer the question based on the following context.
    If you cannot find the answer in the context, say "I don't have enough information."

    Context:
    {context}"""),
    ("human", "{question}")
])

# Critique / Self-reflection prompt
CRITIQUE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a strict critic. Evaluate the answer for accuracy, completeness, and hallucinations."),
    MessagesPlaceholder(variable_name="messages")
])