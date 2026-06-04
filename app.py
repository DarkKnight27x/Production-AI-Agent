import streamlit as st
import requests
from pathlib import Path
import shutil
from datetime import datetime
import sqlite3
import hashlib

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ── DB ─────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("users.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY, password TEXT, name TEXT)''')
    conn.commit(); conn.close()

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def register_user(username, password, name):
    try:
        conn = sqlite3.connect("users.db")
        conn.execute("INSERT INTO users VALUES (?,?,?)", (username, hash_pw(password), name))
        conn.commit(); conn.close(); return True
    except: return False

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                     (username, hash_pw(password)))
    user = c.fetchone(); conn.close(); return user

init_db()

st.set_page_config(page_title="SJ — AI Assistant", page_icon="🌌",
                   layout="wide", initial_sidebar_state="collapsed")

for k, v in [("logged_in", False), ("username", None), ("name", None),
             ("messages", []), ("summarize_mode", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Inter:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp {
    background: #0C0910 !important;
    font-family: 'Inter', sans-serif !important;
    color: #E2E4EF; overflow-x: hidden;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── AUTH LAYOUT ── */
.auth-page .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Auth card shell */
.auth-shell {
    width: 88%; max-width: 1000px;
    min-height: 680px;
    margin: 36px auto;
    background: #000;
    border: 1px solid rgba(255,255,255,0.75);
    border-radius: 24px;
    display: flex; flex-direction: column; align-items: center;
    padding: 72px 40px 40px;
    position: relative;
}
.auth-logo-wrap {
    width: 64px; height: 64px; border-radius: 18px;
    background: linear-gradient(135deg, #6D5FFA, #D946A8);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 1.4rem; color: white;
    box-shadow: 0 4px 28px rgba(109,95,250,0.55);
    margin-bottom: 24px;
    font-family: 'Sora', sans-serif;
}
.auth-title {
    font-family: 'Sora', sans-serif !important;
    font-size: 3rem; font-weight: 600; color: #fff;
    letter-spacing: -0.02em; margin-bottom: 8px; text-align: center;
}
.auth-sub {
    font-family: 'Inter', sans-serif;
    font-size: 1rem; color: rgba(255,255,255,0.5);
    text-align: center; margin-bottom: 0;
}
.auth-divider {
    width: 78%; height: 1px;
    background: rgba(255,255,255,0.2);
    margin: 40px 0 32px;
}

/* Override Streamlit defaults on auth page */
.auth-page div[data-testid="stTextInput"] input,
div[data-baseweb="input"] input {
    background: transparent !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
}
div[data-baseweb="input"] {
    background: transparent !important;
}
div[data-testid="stTextInput"] label {
    color: rgba(255,255,255,0.8) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
}
div[data-testid="stTextInput"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] > div:focus-within {
    box-shadow: none !important;
    border: none !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(109,95,250,0.7) !important;
    box-shadow: 0 0 0 3px rgba(109,95,250,0.15) !important;
    outline: none !important;
}

/* Submit buttons on auth page */
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #6D5FFA, #D946A8) !important;
    border: none !important; border-radius: 12px !important;
    color: white !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important; font-weight: 500 !important;
    width: 100% !important; padding: 12px !important;
    box-shadow: 0 4px 20px rgba(109,95,250,0.4) !important;
    transition: opacity 0.15s, transform 0.15s !important;
    margin-top: 8px !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    opacity: 0.88 !important; transform: translateY(-1px) !important;
}

/* Tabs on auth page */
div[data-testid="stTabs"] {
    width: 100%;
}
div[data-testid="stTabs"] [role="tablist"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    gap: 4px !important;
}
div[data-testid="stTabs"] button[role="tab"] {
    background: transparent !important;
    border: none !important; border-radius: 9px !important;
    color: rgba(255,255,255,0.5) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 400 !important;
    padding: 8px 24px !important;
    transition: all 0.18s !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: rgba(109,95,250,0.25) !important;
    color: #C4B5FD !important;
    font-weight: 500 !important;
}
div[data-testid="stTabs"] [role="tabpanel"] {
    padding-top: 24px !important;
}

/* Alert/error */
div[data-testid="stAlert"] {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.25) !important;
    border-radius: 10px !important;
}
div[data-testid="stAlert"][data-baseweb="notification"] {
    color: #FCA5A5 !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #080610 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
    overflow: hidden !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important; overflow: hidden !important;
    height: 100vh !important; display: flex !important; flex-direction: column !important;
}
section[data-testid="stSidebar"] ::-webkit-scrollbar { display: none !important; }
section[data-testid="stSidebar"] { scrollbar-width: none !important; }
.sj-logo {
    padding: 18px 20px 14px; display: flex; align-items: center; gap: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 6px; flex-shrink: 0;
}
.sj-logo-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #6D5FFA 0%, #D946A8 100%);
    border-radius: 12px; display: flex; align-items: center; justify-content: center;
    font-size: 0.88rem; font-weight: 700; color: white;
    box-shadow: 0 4px 20px rgba(109,95,250,0.45); flex-shrink: 0;
    animation: iconPulse 3s ease-in-out infinite;
}
@keyframes iconPulse {
    0%,100% { box-shadow: 0 4px 20px rgba(109,95,250,0.45); }
    50%      { box-shadow: 0 4px 32px rgba(109,95,250,0.7), 0 0 0 4px rgba(109,95,250,0.12); }
}
.sj-logo-name { font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:600; color:#fff; }
.sj-logo-tag  { font-size:0.63rem; color:#555C7A; letter-spacing:0.1em; margin-top:2px; }

.stButton > button {
    background: transparent !important; border: none !important;
    color: #6B728E !important; text-align: left !important;
    padding: 10px 20px !important; border-radius: 10px !important;
    width: calc(100% - 16px) !important; margin: 1px 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.87rem !important;
    font-weight: 400 !important; transition: all 0.18s ease !important; flex-shrink: 0 !important;
}
.stButton > button:hover {
    background: rgba(109,95,250,0.1) !important; color: #C4C8E4 !important; padding-left: 26px !important;
}
.stButton > button:focus { box-shadow: none !important; outline: none !important; }
.sj-label {
    padding: 8px 22px 4px; font-size: 0.63rem; font-weight: 600;
    color: #2E3350; letter-spacing: 0.14em; text-transform: uppercase; flex-shrink: 0;
}
.sj-sep {
    height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
    margin: 6px 16px; flex-shrink: 0;
}
.sj-hist {
    padding: 7px 22px; font-size: 0.77rem; color: #4A5068;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    cursor: pointer; border-left: 2px solid transparent; transition: all 0.15s;
}
.sj-hist:hover { color:#9BA3C4; border-left-color:rgba(109,95,250,0.5); background:rgba(109,95,250,0.04); }
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(109,95,250,0.2) !important;
    border-radius: 12px !important; padding: 6px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] { margin: 0 8px !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploader"] small { display: none !important; }
.sj-profile {
    padding: 12px 18px; display: flex; align-items: center; gap: 12px;
    border-top: 1px solid rgba(255,255,255,0.05); flex-shrink: 0;
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
.sj-dot { width:5px; height:5px; border-radius:50%; background:#6D5FFA; display:inline-block; animation: dotGlow 2s ease-in-out infinite; }
@keyframes dotGlow {
    0%,100% { box-shadow: 0 0 0 0 rgba(109,95,250,0); }
    50%      { box-shadow: 0 0 6px 2px rgba(109,95,250,0.55); }
}

/* ── MAIN APP ── */
.main-page .block-container {
    padding: 2rem 4rem 8rem 4rem !important;
    max-width: 1200px !important; margin: 0 auto !important;
}

/* Chat avatars hidden */
div[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"],
div[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"],
div[data-testid="stChatMessage"] [data-testid*="chatAvatarIcon"] {
    display: none !important; width: 0 !important; height: 0 !important;
    margin: 0 !important; padding: 0 !important; overflow: hidden !important;
}

@keyframes fadeUp { from{opacity:0;transform:translateY(10px);} to{opacity:1;transform:translateY(0);} }
div[data-testid="stChatMessage"] {
    background: transparent !important; border: none !important;
    padding: 6px 0 !important; animation: fadeUp 0.28s ease;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent {
    background: linear-gradient(135deg, #6D5FFA 0%, #A855F7 100%) !important;
    border: none !important; border-radius: 20px 20px 4px 20px !important;
    padding: 14px 18px !important; box-shadow: 0 4px 24px rgba(109,95,250,0.35) !important;
    max-width: 68% !important; margin-left: auto !important;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: #FFFFFF !important; font-size: 0.94rem !important; line-height: 1.7 !important;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 20px 20px 20px 4px !important; padding: 14px 18px !important;
    backdrop-filter: blur(10px) !important; max-width: 72% !important;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p {
    color: #D4D7EE !important; font-size: 0.94rem !important; line-height: 1.78 !important;
}
div[data-testid="column"] .stButton > button {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 20px !important; padding: 24px 22px !important;
    color: #CDD0E8 !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important; text-align: left !important;
    white-space: pre-wrap !important; line-height: 1.65 !important;
    height: auto !important; min-height: 120px !important;
    width: 100% !important; margin: 0 !important; transition: all 0.22s ease !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: rgba(109,95,250,0.08) !important;
    border-color: rgba(109,95,250,0.35) !important; transform: translateY(-3px) !important;
    box-shadow: 0 14px 45px rgba(109,95,250,0.15) !important; color: #E2E4EF !important;
}
.sum-panel {
    background: linear-gradient(145deg, rgba(109,95,250,0.06), rgba(217,70,168,0.03));
    border: 1px solid rgba(109,95,250,0.2); border-radius: 20px;
    padding: 28px 32px; margin-top: 20px; animation: fadeUp 0.25s ease;
}
.sum-panel-title { font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:600; color:#E2E4EF; margin-bottom:4px; }
.sum-panel-sub { font-size:0.83rem; color:#555C7A; margin-bottom:22px; }
div[data-testid="stSelectbox"] label { color:#7880A0 !important; font-size:0.82rem !important; }
div[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important; color: #CDD0E8 !important;
}
div[data-testid="stFileUploader"] > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(109,95,250,0.25) !important; border-radius: 14px !important;
}
div[data-testid="stBottom"] {
    background: linear-gradient(to top, #0C0910 60%, rgba(12,9,16,0.8) 82%, transparent) !important;
    border: none !important; padding: 20px 4rem 28px !important;
}
div[data-testid="stBottom"] > div { max-width: 1200px !important; margin: 0 auto !important; background: transparent !important; }
div[data-testid="stChatInputContainer"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 20px !important; padding: 6px 10px !important;
    backdrop-filter: blur(24px) !important;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stChatInputContainer"]:focus-within {
    border-color: rgba(109,95,250,0.55) !important;
    box-shadow: 0 0 0 4px rgba(109,95,250,0.1), 0 8px 40px rgba(0,0,0,0.5) !important;
}
div[data-testid="stChatInputContainer"] textarea {
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: #E2E4EF !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.94rem !important; caret-color: #6D5FFA !important;
}
div[data-testid="stChatInputContainer"] textarea::placeholder { color: #35304A !important; }
div[data-testid="stChatInputContainer"] button {
    background: linear-gradient(135deg, #6D5FFA, #D946A8) !important;
    border: none !important; border-radius: 12px !important;
    box-shadow: 0 4px 16px rgba(109,95,250,0.4) !important;
}
div[data-testid="stChatInputContainer"] button:hover { opacity: 0.88 !important; transform: scale(0.96) !important; }
div[data-testid="stDownloadButton"] button {
    background: rgba(109,95,250,0.12) !important; border: 1px solid rgba(109,95,250,0.25) !important;
    color: #9B94F5 !important; border-radius: 10px !important;
    width: calc(100% - 16px) !important; margin: 2px 8px !important; font-size: 0.85rem !important;
}
.stSpinner > div { border-top-color: #6D5FFA !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    # Center everything
    st.markdown("""
    <style>
    .block-container { padding: 40px 0 0 0 !important; max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

    # Logo + title centered
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        # Card border via container
        st.markdown("""
        <div style="
            background:#000;
            border:1px solid rgba(255,255,255,0.75);
            border-radius:24px;
            padding:64px 48px 48px;
            text-align:center;
            margin-bottom:0;
        ">
            <div style="
                width:64px;height:64px;border-radius:18px;
                background:linear-gradient(135deg,#6D5FFA,#D946A8);
                display:flex;align-items:center;justify-content:center;
                font-weight:700;font-size:1.4rem;color:white;
                margin:0 auto 24px;
                box-shadow:0 4px 28px rgba(109,95,250,0.55);
                font-family:'Sora',sans-serif;
            ">SJ</div>
            <div style="font-family:'Sora',sans-serif;font-size:2.6rem;font-weight:600;color:#fff;letter-spacing:-0.02em;margin-bottom:8px;">
                Welcome to SJ
            </div>
            <div style="font-size:1rem;color:rgba(255,255,255,0.45);margin-bottom:40px;">
                Your Intelligent AI Assistant
            </div>
            <div style="height:1px;background:rgba(255,255,255,0.15);margin-bottom:36px;"></div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["   🔑  Login   ", "   ✨  Sign Up   "])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Login →", use_container_width=True):
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.name = user[2]
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

        with tab2:
            with st.form("register_form"):
                new_name = st.text_input("Full Name", placeholder="Your full name")
                new_user = st.text_input("Username", placeholder="Choose a username")
                new_pass = st.text_input("Password", type="password", placeholder="Choose a password")
                if st.form_submit_button("Create Account →", use_container_width=True):
                    if new_name and new_user and new_pass:
                        if register_user(new_user, new_pass, new_name):
                            st.success("✅ Account created! Please login.")
                        else:
                            st.error("Username already taken")
                    else:
                        st.error("Please fill all fields")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
.block-container {
    padding: 2rem 4rem 8rem 4rem !important;
    max-width: 1200px !important; margin: 0 auto !important;
}
</style>
""", unsafe_allow_html=True)

display_name = st.session_state.name.split()[0] if st.session_state.name else "User"
initials = "".join([w[0].upper() for w in st.session_state.name.split()[:2]]) if st.session_state.name else "U"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sj-logo">
        <div class="sj-logo-icon">SJ</div>
        <div><div class="sj-logo-name">SJ</div><div class="sj-logo-tag">AI ASSISTANT</div></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⌂  Home", use_container_width=True, key="home_btn"):
        st.session_state.messages = []; st.session_state.summarize_mode = False; st.rerun()

    if st.button("◎  Explore", use_container_width=True, key="explore_btn"):
        q = "What are the most exciting topics to explore in AI, science, and technology right now?"
        st.session_state.messages.append({"role": "user", "content": q})
        with st.spinner(""):
            try:
                resp = requests.post(f"{BACKEND_URL}/chat", json={"question": q, "history": []}, timeout=60)
                answer = resp.json().get("answer", "No response")
            except: answer = "Backend not running"
        st.session_state.messages.append({"role": "assistant", "content": answer}); st.rerun()

    if st.button("◷  History", use_container_width=True, key="history_btn"):
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

    uploaded = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True,
                                 label_visibility="collapsed", key="sidebar_uploader")
    if uploaded:
        for file in uploaded:
            Path("data").mkdir(exist_ok=True)
            with open(Path("data") / file.name, "wb") as f: f.write(file.getbuffer())
        st.success(f"✅ {len(uploaded)} file(s) uploaded")

    if st.button("↻  Re-ingest Documents", use_container_width=True, key="reingest_btn"):
        try:
            r = requests.post(f"{BACKEND_URL}/ingest", timeout=30)
            st.success("✅ Done") if r.status_code == 200 else st.error("Failed")
        except: st.error("Backend not running")

    if st.button("⊗  Clear & Rebuild Index", use_container_width=True, key="clear_btn"):
        try:
            if Path("faiss_index").exists(): shutil.rmtree("faiss_index")
            requests.post(f"{BACKEND_URL}/ingest", timeout=30); st.success("✅ Index reset")
        except: st.error("Error")

    st.markdown('<div class="sj-sep"></div>', unsafe_allow_html=True)

    if st.button("✦  New Chat", use_container_width=True, key="new_chat_btn"):
        st.session_state.messages = []; st.session_state.summarize_mode = False; st.rerun()

    if st.button("↗  Export Chat", use_container_width=True, key="export_btn"):
        if st.session_state.messages:
            chat_text = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            st.download_button("⬇ Download", chat_text,
                f"SJ_Chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)

    if st.button("← Logout", use_container_width=True, key="logout_btn"):
        for k in ["logged_in","username","name","messages","summarize_mode"]:
            st.session_state[k] = False if k=="logged_in" else ([] if k=="messages" else (False if k=="summarize_mode" else None))
        st.rerun()

    st.markdown(f"""
    <div class="sj-profile">
        <div class="sj-avatar">{initials}</div>
        <div><div class="sj-pname">{st.session_state.name}</div>
        <div class="sj-pplan"><span class="sj-dot"></span> Free Plan</div></div>
    </div>
    """, unsafe_allow_html=True)

# ── Main area ──────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")

    st.markdown(f"""
    <style>
    @keyframes glowPulse {{ 0%,100%{{transform:scale(1);opacity:0.6;}} 50%{{transform:scale(1.35);opacity:1;}} }}
    @keyframes orbFloat  {{ 0%,100%{{transform:translateY(0) scale(1);}} 50%{{transform:translateY(-12px) scale(1.04);}} }}
    </style>
    <div style="text-align:center;padding:72px 0 52px;">
        <div style="width:130px;height:130px;margin:0 auto 40px;position:relative;">
            <div style="position:absolute;inset:-24px;border-radius:50%;
                background:radial-gradient(circle,rgba(109,95,250,0.22) 0%,transparent 70%);
                animation:glowPulse 4s ease-in-out infinite;"></div>
            <div style="width:130px;height:130px;border-radius:50%;
                background:radial-gradient(circle at 32% 28%,#D4C8FF 0%,#8B7FF8 22%,#D946A8 58%,#F43F5E 90%);
                box-shadow:0 0 0 1px rgba(167,139,250,0.2),0 0 55px rgba(109,95,250,0.6),0 0 130px rgba(217,70,168,0.35);
                animation:orbFloat 7s ease-in-out infinite;position:relative;z-index:1;"></div>
        </div>
        <div style="font-family:'Sora',sans-serif;font-size:2.9rem;font-weight:600;
            background:linear-gradient(135deg,#FFFFFF 0%,#A8AECF 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            letter-spacing:-0.04em;line-height:1.2;margin-bottom:12px;">{greeting}, {display_name}.</div>
        <div style="font-size:1rem;color:#4A5068;font-weight:300;">How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📄  Summarize Document\n\nUpload a PDF and get a structured AI summary instantly", key="btn_summarize", use_container_width=True):
            st.session_state.summarize_mode = not st.session_state.summarize_mode; st.rerun()
    with c2:
        if st.button("🔍  Deep Research\n\nAsk complex questions across all your uploaded files", key="btn_research", use_container_width=True):
            q = "I want to do deep research on my uploaded documents. What can you help me find?"
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner(""):
                try:
                    resp = requests.post(f"{BACKEND_URL}/chat", json={"question": q, "history": []}, timeout=60)
                    answer = resp.json().get("answer", "No response")
                except: answer = "Backend not running"
            st.session_state.messages.append({"role": "assistant", "content": answer}); st.rerun()
    with c3:
        if st.button("💡  Brainstorm Ideas\n\nGenerate creative ideas on any topic you have in mind", key="btn_brainstorm", use_container_width=True):
            q = "Let's brainstorm creative ideas together. What topic should we explore?"
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner(""):
                try:
                    resp = requests.post(f"{BACKEND_URL}/chat", json={"question": q, "history": []}, timeout=60)
                    answer = resp.json().get("answer", "No response")
                except: answer = "Backend not running"
            st.session_state.messages.append({"role": "assistant", "content": answer}); st.rerun()

    if st.session_state.summarize_mode:
        st.markdown("""<div class="sum-panel">
            <div class="sum-panel-title">📄 Summarize a Document</div>
            <div class="sum-panel-sub">Upload a PDF from your device, or select one already ingested.</div>
        </div>""", unsafe_allow_html=True)
        data_dir = Path("data"); data_dir.mkdir(exist_ok=True)
        new_upload = st.file_uploader("Upload a PDF from your device", type="pdf", key="modal_uploader")
        if new_upload:
            with open(data_dir / new_upload.name, "wb") as fh: fh.write(new_upload.getbuffer())
            st.success(f"✅ {new_upload.name} ready")
        pdf_names = [f.name for f in sorted(data_dir.glob("*.pdf"))]
        if new_upload and new_upload.name not in pdf_names: pdf_names.insert(0, new_upload.name)
        selected_pdf = None
        if pdf_names:
            selected_pdf = st.selectbox("Or select an already-uploaded document",
                options=pdf_names, format_func=lambda x: f"📄  {x}", key="summarize_select")
        else: st.info("No PDFs found — upload one above.")
        col_ok, col_cancel = st.columns([2, 1])
        with col_ok:
            confirm = st.button("✦  Summarize Now", use_container_width=True, key="modal_confirm")
        with col_cancel:
            if st.button("✕  Close", use_container_width=True, key="modal_cancel"):
                st.session_state.summarize_mode = False; st.rerun()
        if confirm and selected_pdf:
            st.session_state.summarize_mode = False
            user_msg = f"📄 Summarize document: **{selected_pdf}**"
            backend_q = (f"Please provide a detailed, well-structured summary of the document: {selected_pdf}. "
                         "Include: 1) Overview, 2) Key Topics, 3) Important Details, 4) Conclusions.")
            st.session_state.messages.append({"role": "user", "content": user_msg})
            with st.spinner("Summarizing..."):
                try:
                    history_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                    resp = requests.post(f"{BACKEND_URL}/chat", json={"question": backend_q, "history": history_payload}, timeout=120)
                    answer = resp.json().get("answer", "Something went wrong.")
                except Exception: answer = "Backend not running. Start with `python -m src.main`"
            st.session_state.messages.append({"role": "assistant", "content": answer}); st.rerun()

else:
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

if prompt := st.chat_input("Message SJ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner(""):
        try:
            history_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            resp = requests.post(f"{BACKEND_URL}/chat", json={"question": prompt, "history": history_payload}, timeout=60)
            answer = resp.json().get("answer", "Something went wrong.")
        except Exception: answer = "Backend not running. Start with `python -m src.main`"
    st.session_state.messages.append({"role": "assistant", "content": answer}); st.rerun()