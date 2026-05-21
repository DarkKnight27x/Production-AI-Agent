import streamlit as st
import requests
from pathlib import Path
import shutil
from datetime import datetime

st.set_page_config(
    page_title="SJ — AI Assistant",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #0D0D0F !important;
    font-family: 'DM Sans', sans-serif;
    color: #E8E8EC;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2rem 2rem 2rem !important;
    max-width: 860px !important;
    margin: 0 auto !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #111114 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

.sidebar-logo {
    padding: 28px 20px 8px;
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.02em;
    display: flex;
    align-items: center;
    gap: 10px;
}
.logo-dot {
    width: 22px; height: 22px;
    background: linear-gradient(135deg, #7C6AF7, #EC4899);
    border-radius: 6px;
    flex-shrink: 0;
}
.sidebar-nav {
    padding: 16px 12px;
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 8px;
    font-size: 0.88rem;
    color: #9199A6;
    cursor: pointer;
}
.nav-item.active { background: rgba(124,106,247,0.15); color: #A99FF5; }
.sidebar-sep {
    height: 1px;
    background: rgba(255,255,255,0.05);
    margin: 8px 16px;
}
.sidebar-label {
    padding: 12px 20px 4px;
    font-size: 0.68rem;
    font-weight: 500;
    color: #4A5160;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.history-item {
    padding: 6px 20px;
    font-size: 0.8rem;
    color: #6B7280;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
}
.user-profile {
    padding: 16px 20px;
    border-top: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 12px;
}
.u-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7C6AF7, #EC4899);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 600; color: white;
    flex-shrink: 0;
}
.u-name { font-size: 0.82rem; font-weight: 500; color: #D1D5DB; }
.u-plan { font-size: 0.7rem; color: #6B7280; }

/* ── Orb ── */
.orb-wrap {
    width: 120px; height: 120px;
    margin: 0 auto 28px;
    position: relative;
}
.orb {
    width: 120px; height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%,
        #C4B5FD 0%, #818CF8 30%, #EC4899 65%, #F43F5E 90%);
    box-shadow: 0 0 70px rgba(167,139,250,0.55), 0 0 140px rgba(236,72,153,0.3);
    animation: orbFloat 6s ease-in-out infinite;
}
@keyframes orbFloat {
    0%,100% { transform: translateY(0) scale(1); }
    50%      { transform: translateY(-9px) scale(1.04); }
}

/* ── Greeting ── */
.greeting-text {
    font-family: 'Sora', sans-serif;
    font-size: 2.3rem;
    font-weight: 500;
    color: #F0F0F5;
    text-align: center;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}
.greeting-sub {
    font-size: 1rem;
    color: #6B7280;
    text-align: center;
    margin-bottom: 40px;
}

/* ── Cards ── */
.cards-row {
    display: flex;
    gap: 14px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 40px;
}
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 20px;
    width: 210px;
    cursor: pointer;
    transition: all 0.2s;
}
.card:hover {
    background: rgba(255,255,255,0.07);
    border-color: rgba(167,139,250,0.35);
    transform: translateY(-2px);
}
.card-title {
    font-family: 'Sora', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: #E8E8EC;
    margin-bottom: 7px;
}
.card-desc { font-size: 0.77rem; color: #6B7280; line-height: 1.5; }

/* ── Chat messages ── */
div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 6px 0 !important;
}
div[data-testid="stChatMessage"] p { font-size: 0.92rem; line-height: 1.7; }

/* ── Chat input bar ── */
div[data-testid="stBottom"] {
    display: block !important;
    visibility: visible !important;
    background: #0D0D0F !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    padding: 14px 10% 20px !important;
    left: 0 !important; right: 0 !important;
    box-shadow: none !important;
}
div[data-testid="stBottom"] > div {
    background: transparent !important;
    max-width: 760px !important;
    margin: 0 auto !important;
}
div[data-testid="stChatInputContainer"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    padding: 4px 8px !important;
}
div[data-testid="stChatInputContainer"]:focus-within {
    border-color: rgba(124,106,247,0.6) !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.1) !important;
}
div[data-testid="stChatInputContainer"] textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #E8E8EC !important;
    font-family: "DM Sans", sans-serif !important;
    font-size: 0.92rem !important;
}
div[data-testid="stChatInputContainer"] textarea::placeholder { color: #4A5160 !important; }
div[data-testid="stChatInputContainer"] button {
    background: linear-gradient(135deg, #7C6AF7, #EC4899) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
}



/* Sidebar buttons */
.stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #9199A6 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    width: 100% !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: rgba(124,106,247,0.12) !important;
    border-color: rgba(124,106,247,0.3) !important;
    color: #A99FF5 !important;
}

/* File uploader */
section[data-testid="stSidebar"] .stFileUploader > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #7C6AF7 !important; }



</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-dot"></div>SJ
    </div>
    <div class="sidebar-nav">
        <div class="nav-item active">⌂ &nbsp;Home</div>
        <div class="nav-item">◫ &nbsp;Templates</div>
        <div class="nav-item">◎ &nbsp;Explore</div>
        <div class="nav-item">◷ &nbsp;History</div>
    </div>
    <div class="sidebar-sep"></div>
    """, unsafe_allow_html=True)

    if st.session_state.messages:
        st.markdown('<div class="sidebar-label">Recent</div>', unsafe_allow_html=True)
        user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        for msg in user_msgs[-5:][::-1]:
            preview = msg[:36] + "…" if len(msg) > 36 else msg
            st.markdown(f'<div class="history-item">{preview}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Documents</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("PDFs", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
    if uploaded:
        for file in uploaded:
            Path("data").mkdir(exist_ok=True)
            with open(Path("data") / file.name, "wb") as f:
                f.write(file.getbuffer())
        st.success(f"✅ {len(uploaded)} file(s) uploaded")

    if st.button("↻  Re-ingest Documents"):
        try:
            r = requests.post("http://localhost:8000/ingest", timeout=30)
            st.success("✅ Done") if r.status_code == 200 else st.error("Failed")
        except:
            st.error("Backend not running")

    if st.button("⊗  Clear & Rebuild Index"):
        try:
            if Path("faiss_index").exists():
                shutil.rmtree("faiss_index")
            requests.post("http://localhost:8000/ingest", timeout=30)
            st.success("✅ Index reset")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)

    if st.button("✦  New Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div class="user-profile">
        <div class="u-avatar">Sk</div>
        <div>
            <div class="u-name">Sk</div>
            <div class="u-plan">Free Plan</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Main area ──────────────────────────────────────────────────────────────────
hour = datetime.now().hour
greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")

if not st.session_state.messages:
    # Welcome screen
    st.markdown(f"""
    <div style="text-align:center; padding: 48px 0 0;">
        <div class="orb-wrap"><div class="orb"></div></div>
        <div class="greeting-text">{greeting}, Sk.</div>
        <div class="greeting-sub">Can I help you with anything?</div>
    </div>
    <div class="cards-row">
        <div class="card">
            <div class="card-title">📄 Summarize Document</div>
            <div class="card-desc">Upload a PDF and get a concise summary instantly</div>
        </div>
        <div class="card">
            <div class="card-title">🔍 Deep Research</div>
            <div class="card-desc">Ask complex questions across your uploaded files</div>
        </div>
        <div class="card">
            <div class="card-title">💡 Brainstorm Ideas</div>
            <div class="card-desc">Generate creative ideas on any topic you have in mind</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Chat history
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Message SJ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner(""):
        try:
            history_payload = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]
            resp = requests.post(
                "http://localhost:8000/chat",
                json={"question": prompt, "history": history_payload},
                timeout=60
            )
            answer = resp.json().get("answer", "Something went wrong.")
        except Exception as e:
            answer = f"Backend not running. Start with `python -m src.main`\n{e}"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()