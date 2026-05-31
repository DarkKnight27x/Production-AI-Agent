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
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Inter:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #0C0910 !important;
    font-family: 'Inter', sans-serif;
    color: #E2E4EF;
    overflow-x: hidden;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 2rem 4rem 8rem 4rem !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* ═══════════════════════════════════
   SIDEBAR
═══════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: #080610 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
    overflow: hidden !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    overflow: hidden !important;
    height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
}
section[data-testid="stSidebar"] ::-webkit-scrollbar { display: none !important; }
section[data-testid="stSidebar"] { scrollbar-width: none !important; }
 
.sj-logo {
    padding: 18px 20px 14px;
    display: flex; align-items: center; gap: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 6px; flex-shrink: 0;
}
.sj-logo-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #6D5FFA 0%, #D946A8 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.88rem; font-weight: 700; color: white;
    box-shadow: 0 4px 20px rgba(109,95,250,0.45);
    flex-shrink: 0;
    animation: iconPulse 3s ease-in-out infinite;
}
@keyframes iconPulse {
    0%,100% { box-shadow: 0 4px 20px rgba(109,95,250,0.45); }
    50%      { box-shadow: 0 4px 32px rgba(109,95,250,0.7), 0 0 0 4px rgba(109,95,250,0.12); }
}
.sj-logo-name { font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:600; color:#fff; }
.sj-logo-tag  { font-size:0.63rem; color:#555C7A; letter-spacing:0.1em; margin-top:2px; }
 
.stButton > button {
    background: transparent !important;
    border: none !important;
    color: #6B728E !important;
    text-align: left !important;
    padding: 10px 20px !important;
    border-radius: 10px !important;
    width: calc(100% - 16px) !important;
    margin: 1px 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
    font-weight: 400 !important;
    transition: all 0.18s ease !important;
    flex-shrink: 0 !important;
}
.stButton > button:hover {
    background: rgba(109,95,250,0.1) !important;
    color: #C4C8E4 !important;
    padding-left: 26px !important;
}
.stButton > button:focus { box-shadow: none !important; outline: none !important; }
 
.sj-label {
    padding: 8px 22px 4px;
    font-size: 0.63rem; font-weight: 600;
    color: #2E3350; letter-spacing: 0.14em;
    text-transform: uppercase; flex-shrink: 0;
}
.sj-sep {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
    margin: 6px 16px; flex-shrink: 0;
}
.sj-hist {
    padding: 7px 22px;
    font-size: 0.77rem; color: #4A5068;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    cursor: pointer; border-left: 2px solid transparent;
    transition: all 0.15s;
}
.sj-hist:hover { color: #9BA3C4; border-left-color: rgba(109,95,250,0.5); background: rgba(109,95,250,0.04); }
 
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(109,95,250,0.2) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    transition: border-color 0.2s !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div:hover {
    border-color: rgba(109,95,250,0.45) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] { margin: 0 8px !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploader"] small { display: none !important; }
 
.sj-profile {
    padding: 12px 18px;
    display: flex; align-items: center; gap: 12px;
    border-top: 1px solid rgba(255,255,255,0.05);
    flex-shrink: 0;
}
.sj-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, #6D5FFA, #D946A8);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 700; color: white; flex-shrink: 0;
    box-shadow: 0 2px 14px rgba(109,95,250,0.4);
}
.sj-pname { font-size: 0.84rem; font-weight: 500; color: #C8CCDF; }
.sj-pplan { font-size: 0.68rem; color: #555C7A; display:flex; align-items:center; gap:4px; margin-top:2px; }
.sj-dot {
    width:5px; height:5px; border-radius:50%;
    background:#6D5FFA; display:inline-block;
    animation: dotGlow 2s ease-in-out infinite;
}
@keyframes dotGlow {
    0%,100% { box-shadow: 0 0 0 0 rgba(109,95,250,0); }
    50%      { box-shadow: 0 0 6px 2px rgba(109,95,250,0.55); }
}

/* STRONG AVATAR REMOVAL */
div[data-testid="stChatMessage"] [data-testid*="chatAvatarIcon"],
div[data-testid="stChatMessage"] > div:first-child > div:first-child,
div[data-testid="stChatMessage"] > div:first-child,
div[data-testid="stChatMessage"] .stChatMessageAvatar {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}

div[data-testid="stChatMessage"] {
    padding-left: 16px !important;
    padding-right: 16px !important;
}

/* CHAT BUBBLES */
div[data-testid="stChatMessage"] {
    border-radius: 18px !important;
    padding: 16px 20px !important;
    margin: 10px 0 !important;
    max-width: 82% !important;
}

div[data-testid="stChatMessage"][data-testid*="user"] {
    background: linear-gradient(135deg, #6D5FFA, #8B5CF6) !important;
    color: white !important;
    margin-left: auto !important;
}

div[data-testid="stChatMessage"]:not([data-testid*="user"]) {
    background: #12121A !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #E8E8F0 !important;
    margin-right: auto !important;
}

/* CHAT INPUT */
div[data-testid="stBottom"] {
    background: linear-gradient(to top, #0C0910 60%, rgba(12,9,16,0.8) 82%, transparent) !important;
    padding: 20px 4rem 28px !important;
}
div[data-testid="stChatInputContainer"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 20px !important;
}

/* Your other styles */
.sj-logo { padding: 18px 20px 14px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 6px; flex-shrink: 0; }
.sj-logo-icon { width: 40px; height: 40px; background: linear-gradient(135deg, #6D5FFA 0%, #D946A8 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 0.88rem; font-weight: 700; color: white; box-shadow: 0 4px 20px rgba(109,95,250,0.45); flex-shrink: 0; }
.sj-logo-name { font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:600; color:#fff; }
.sj-logo-tag { font-size:0.63rem; color:#555C7A; letter-spacing:0.1em; margin-top:2px; }

.stButton > button {
    background: transparent !important;
    border: none !important;
    color: #6B728E !important;
    text-align: left !important;
    padding: 10px 20px !important;
    border-radius: 10px !important;
    width: calc(100% - 16px) !important;
    margin: 1px 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
    font-weight: 400 !important;
    transition: all 0.18s ease !important;
}

.stButton > button:hover {
    background: rgba(109,95,250,0.1) !important;
    color: #C4C8E4 !important;
}
/* Welcome Screen Cards */
.cards-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 60px;
    padding: 0 40px;
}

.card {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 28px 24px !important;
    transition: all 0.3s ease !important;
    cursor: pointer;
}

.card:hover {
    transform: translateY(-6px) !important;
    border-color: rgba(109,95,250,0.4) !important;
    box-shadow: 0 20px 40px rgba(109,95,250,0.15) !important;
}
/* ═══════════════════════════════════
   CARD BUTTONS
═══════════════════════════════════ */
div[data-testid="column"] .stButton > button {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 20px !important;
    padding: 24px 22px !important;
    color: #CDD0E8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
    text-align: left !important;
    white-space: pre-wrap !important;
    line-height: 1.65 !important;
    height: auto !important;
    min-height: 120px !important;
    width: 100% !important;
    margin: 0 !important;
    transition: all 0.22s ease !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: rgba(109,95,250,0.08) !important;
    border-color: rgba(109,95,250,0.35) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 14px 45px rgba(109,95,250,0.15) !important;
    color: #E2E4EF !important;
}
/* ═══════════════════════════════════
   SUMMARIZE PANEL
═══════════════════════════════════ */
.sum-panel {
    background: linear-gradient(145deg, rgba(109,95,250,0.06), rgba(217,70,168,0.03));
    border: 1px solid rgba(109,95,250,0.2);
    border-radius: 20px; padding: 28px 32px;
    margin-top: 20px; animation: fadeUp 0.25s ease;
}
.sum-panel-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.1rem; font-weight: 600; color: #E2E4EF; margin-bottom: 4px;
}
.sum-panel-sub { font-size: 0.83rem; color: #555C7A; margin-bottom: 22px; }
 
div[data-testid="stSelectbox"] label { color: #7880A0 !important; font-size: 0.82rem !important; }
div[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important; color: #CDD0E8 !important;
}
 
/* File uploader in main area */
div[data-testid="stFileUploader"] > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(109,95,250,0.25) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(109,95,250,0.5) !important;
}

</style>
""", unsafe_allow_html=True)
# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "summarize_mode" not in st.session_state:
    st.session_state.summarize_mode = False
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sj-logo">
        <div class="sj-logo-icon">SJ</div>
        <div>
            <div class="sj-logo-name">SJ</div>
            <div class="sj-logo-tag">AI ASSISTANT</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    if st.button("⌂  Home", use_container_width=True):
        st.session_state.messages = []
        st.session_state.summarize_mode = False
        st.rerun()
 
    if st.button("◎  Explore", use_container_width=True):
        q = "What are the most exciting topics to explore in AI, science, and technology right now?"
        st.session_state.messages.append({"role": "user", "content": q})
        with st.spinner(""):
            try:
                resp = requests.post("http://localhost:8000/chat", json={"question": q, "history": []}, timeout=60)
                answer = resp.json().get("answer", "No response")
            except:
                answer = "Backend not running"
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
 
    if st.button("◷  History", use_container_width=True):
        st.info("Persistent history coming soon.")
 
    if st.session_state.messages:
        st.markdown('<div class="sj-sep"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sj-label">Recent</div>', unsafe_allow_html=True)
        user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        for msg in user_msgs[-4:][::-1]:
            preview = msg[:32] + "…" if len(msg) > 32 else msg
            st.markdown(f'<div class="sj-hist">{preview}</div>', unsafe_allow_html=True)
 
    st.markdown('<div class="sj-sep"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sj-label">Documents</div>', unsafe_allow_html=True)
 
    uploaded = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
    if uploaded:
        for file in uploaded:
            Path("data").mkdir(exist_ok=True)
            with open(Path("data") / file.name, "wb") as f:
                f.write(file.getbuffer())
        st.success(f"✅ {len(uploaded)} file(s) uploaded")
 
    if st.button("↻  Re-ingest Documents", use_container_width=True):
        try:
            r = requests.post("http://localhost:8000/ingest", timeout=30)
            st.success("✅ Done") if r.status_code == 200 else st.error("Failed")
        except:
            st.error("Backend not running")
 
    if st.button("⊗  Clear & Rebuild Index", use_container_width=True):
        try:
            if Path("faiss_index").exists():
                shutil.rmtree("faiss_index")
            requests.post("http://localhost:8000/ingest", timeout=30)
            st.success("✅ Index reset")
        except:
            st.error("Error")
 
    st.markdown('<div class="sj-sep"></div>', unsafe_allow_html=True)
 
    if st.button("✦  New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.summarize_mode = False
        st.rerun()
 
    if st.button("↗  Export Chat", use_container_width=True):
        if st.session_state.messages:
            chat_text = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            st.download_button("⬇ Download", chat_text,
                f"SJ_Chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain", use_container_width=True)
 
    st.markdown("""
    <div class="sj-profile">
        <div class="sj-avatar">Sk</div>
        <div>
            <div class="sj-pname">Sk</div>
            <div class="sj-pplan"><span class="sj-dot"></span> Free Plan</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
# ── Main area ──────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")
 
    st.markdown(f"""
    <div style="text-align:center; padding: 72px 0 52px;">
        <div style="width:130px;height:130px;margin:0 auto 40px;position:relative;">
            <div style="position:absolute;inset:-24px;border-radius:50%;
                background:radial-gradient(circle, rgba(109,95,250,0.22) 0%, transparent 70%);
                animation:glowPulse 4s ease-in-out infinite;"></div>
            <div style="width:130px;height:130px;border-radius:50%;
                background:radial-gradient(circle at 32% 28%, #D4C8FF 0%, #8B7FF8 22%, #D946A8 58%, #F43F5E 90%);
                box-shadow:0 0 0 1px rgba(167,139,250,0.2),0 0 55px rgba(109,95,250,0.6),0 0 130px rgba(217,70,168,0.35);
                animation:orbFloat 7s ease-in-out infinite;position:relative;z-index:1;">
            </div>
        </div>
        <div style="font-family:'Sora',sans-serif;font-size:2.9rem;font-weight:600;
            background:linear-gradient(135deg,#FFFFFF 0%,#A8AECF 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            letter-spacing:-0.04em;line-height:1.2;margin-bottom:12px;">{greeting}, Sk.</div>
        <div style="font-size:1rem;color:#4A5068;font-weight:300;">How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)
 
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📄  Summarize Document\n\nUpload a PDF and get a structured AI summary instantly", key="btn_summarize", use_container_width=True):
            st.session_state.summarize_mode = not st.session_state.summarize_mode
            st.rerun()
    with c2:
        if st.button("🔍  Deep Research\n\nAsk complex questions across all your uploaded files", key="btn_research", use_container_width=True):
            q = "I want to do deep research on my uploaded documents. What can you help me find?"
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner(""):
                try:
                    resp = requests.post("http://localhost:8000/chat", json={"question": q, "history": []}, timeout=60)
                    answer = resp.json().get("answer", "No response")
                except:
                    answer = "Backend not running"
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    with c3:
        if st.button("💡  Brainstorm Ideas\n\nGenerate creative ideas on any topic you have in mind", key="btn_brainstorm", use_container_width=True):
            q = "Let's brainstorm creative ideas together. What topic should we explore?"
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner(""):
                try:
                    resp = requests.post("http://localhost:8000/chat", json={"question": q, "history": []}, timeout=60)
                    answer = resp.json().get("answer", "No response")
                except:
                    answer = "Backend not running"
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
 
    # ── Summarize panel ────────────────────────────────────────────────────────
    if st.session_state.summarize_mode:
        st.markdown("""
        <div class="sum-panel">
            <div class="sum-panel-title">📄 Summarize a Document</div>
            <div class="sum-panel-sub">Upload a PDF from your device, or select one already ingested.</div>
        </div>
        """, unsafe_allow_html=True)
 
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
 
        # File uploader — opens native OS file picker
        new_upload = st.file_uploader(
            "Upload a PDF from your device",
            type="pdf",
            key="modal_uploader"
        )
        if new_upload:
            with open(data_dir / new_upload.name, "wb") as fh:
                fh.write(new_upload.getbuffer())
            st.success(f"✅ {new_upload.name} ready")
 
        # Dropdown of already-ingested PDFs
        pdf_names = [f.name for f in sorted(data_dir.glob("*.pdf"))]
        if new_upload and new_upload.name not in pdf_names:
            pdf_names.insert(0, new_upload.name)
 
        selected_pdf = None
        if pdf_names:
            selected_pdf = st.selectbox(
                "Or select an already-uploaded document",
                options=pdf_names,
                format_func=lambda x: f"📄  {x}",
                key="summarize_select"
            )
        else:
            st.info("No PDFs found — upload one above.")
 
        col_ok, col_cancel = st.columns([2, 1])
        with col_ok:
            confirm = st.button("✦  Summarize Now", use_container_width=True, key="modal_confirm")
        with col_cancel:
            if st.button("✕  Close", use_container_width=True, key="modal_cancel"):
                st.session_state.summarize_mode = False
                st.rerun()
 
        if confirm and selected_pdf:
            st.session_state.summarize_mode = False
            user_msg = f"📄 Summarize document: **{selected_pdf}**"
            backend_q = (
                f"Please provide a detailed, well-structured summary of the document: {selected_pdf}. "
                "Include: 1) Overview, 2) Key Topics, 3) Important Details, 4) Conclusions."
            )
            st.session_state.messages.append({"role": "user", "content": user_msg})
            with st.spinner("Summarizing..."):
                try:
                    history_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                    resp = requests.post("http://localhost:8000/chat",
                        json={"question": backend_q, "history": history_payload}, timeout=120)
                    answer = resp.json().get("answer", "Something went wrong.")
                except Exception:
                    answer = "Backend not running. Start with `python -m src.main`"
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
 
else:
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
 
# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Message SJ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner(""):
        try:
            history_payload = [{"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]]
            resp = requests.post("http://localhost:8000/chat",
                json={"question": prompt, "history": history_payload}, timeout=60)
            answer = resp.json().get("answer", "Something went wrong.")
        except Exception:
            answer = "Backend not running. Start with `python -m src.main`"
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
 