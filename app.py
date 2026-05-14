import streamlit as st
import requests
import time

st.set_page_config(page_title="Production AI Agent", page_icon="🧠", layout="wide")

st.title("🧠 Production AI Agent")
st.caption("**Agentic RAG + General Knowledge** • Built by Sk")

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"question": prompt},
                    timeout=25
                )
                
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Backend returned error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend is not running! Start it with: `python -m src.main`")
                st.info("Tip: Open another terminal and run `python -m src.main`")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Sidebar
with st.sidebar:
    st.header("📁 Documents")
    if st.button("🔄 Re-ingest Documents"):
        try:
            r = requests.post(f"{BACKEND_URL}/ingest")
            if r.status_code == 200:
                st.success("✅ Documents ingested successfully!")
            else:
                st.error("Failed to ingest")
        except:
            st.error("Backend not running")

    st.markdown("---")
    st.caption("FastAPI + LangGraph + FAISS")