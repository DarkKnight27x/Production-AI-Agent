import streamlit as st
import requests
from pathlib import Path
import shutil

st.set_page_config(page_title="Production AI Agent", page_icon="🧠", layout="wide")

st.title("🧠 Production AI Agent")
st.caption("**Agentic RAG + File Upload + Tools** • Built by Sk")

# Persistent chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("📁 Document Management")
    
    # File Upload
    uploaded_files = st.file_uploader(
        "Upload PDF Documents", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            save_path = Path("data") / file.name
            save_path.parent.mkdir(exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())
        st.success(f"✅ Uploaded {len(uploaded_files)} PDF(s)")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Re-ingest Documents"):
            try:
                r = requests.post("http://localhost:8000/ingest", timeout=40)
                if r.status_code == 200:
                    st.success("✅ Documents processed successfully!")
                else:
                    st.error("Ingestion failed")
            except:
                st.error("❌ Backend not running")

    with col2:
        if st.button("🗑️ Clear & Rebuild Index"):
            try:
                if Path("faiss_index").exists():
                    shutil.rmtree("faiss_index")
                st.success("✅ Old index cleared!")
                r = requests.post("http://localhost:8000/ingest", timeout=40)
                if r.status_code == 200:
                    st.success("✅ Fresh index built!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.caption("FastAPI + LangGraph + FAISS")

# ==================== CHAT INTERFACE ====================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={"question": prompt},
                    timeout=60
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", "Sorry, I couldn't process that.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Backend error: {response.status_code}")
            except Exception as e:
                st.error(f"Cannot connect to backend. Make sure backend is running.\nError: {e}")
