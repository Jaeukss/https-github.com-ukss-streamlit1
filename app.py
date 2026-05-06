# -*- coding: utf-8 -*-
import os
import streamlit as st

st.set_page_config(
    page_title="에이블 | Z세대 리브랜딩 AI 비서",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# GLOBAL STYLE
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Pretendard:wght@300;400;500;600;700&display=swap');

/* hide default sidebar nav & hamburger on login */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

html, body, [class*="css"] {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif !important;
}
.stApp {
    background: #F7F4FF !important;
    min-height: 100vh;
}
[data-testid="stAppViewContainer"] { background: #F7F4FF !important; }
.block-container {
    padding-top: 0 !important;
    max-width: 100% !important;
}

/* ── LOGIN LAYOUT ── */
.login-root {
    display: flex;
    min-height: 100vh;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
}
.login-card {
    width: 100%;
    max-width: 480px;
}
.login-logo {
    text-align: center;
    margin-bottom: 2.5rem;
}
.login-wordmark {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(120deg, #C4A8FF 0%, #E94C98 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    line-height: 1;
}
.login-sub {
    font-size: 0.82rem;
    color: #766D8A;
    margin-top: 0.5rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.login-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6F6682;
    margin-bottom: 0.9rem;
}

/* ── ROLE CARDS ── */
.role-btn-wrap { margin-bottom: 0.55rem; }
.role-visual {
    background: #FFFFFF;
    border: 1px solid #DDD3F2;
    border-radius: 16px;
    padding: 1.05rem 1.3rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: border-color 0.18s, transform 0.18s;
    pointer-events: none;
    margin-bottom: -0.1rem;
}
.role-visual:hover { border-color: #B49DFF; transform: translateY(-1px); }
.role-avatar {
    width: 46px; height: 46px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; flex-shrink: 0;
}
.role-info { flex: 1; min-width: 0; }
.role-name {
    font-family: 'Syne', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: #211A32;
}
.role-desc { font-size: 0.75rem; color: #766D8A; margin-top: 2px; }
.role-arrow { color: #8E84A6; font-size: 1rem; }

/* Login page buttons — styled to look like the role card */
.stButton > button {
    background: transparent !important;
    border: 1px solid #DDD3F2 !important;
    border-radius: 16px !important;
    color: #2E2940 !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 1rem 1.3rem !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.18s !important;
    margin-bottom: 0.4rem !important;
}
.stButton > button:hover {
    background: #F2ECFF !important;
    border-color: #B49DFF !important;
    transform: translateY(-1px) !important;
}


/* ── LIGHTER LOGIN READABILITY ── */
.stMarkdown, .stMarkdown p, label { color: #2E2940 !important; }

/* ── FOOTER ── */
.login-footer {
    text-align: center;
    margin-top: 3rem;
    font-size: 0.72rem;
    color: #9B92AD;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ROLE DEFINITIONS  (shared across pages via session_state)
# ══════════════════════════════════════════════════════════════
ROLES = {
    "김부장": {
        "title": "부장", "emoji": "🦁",
        "color": "#3F7CF6", "bg": "#EAF1FF",
        "desc": "전략 총괄 · 최종 결재",
        "access": "full",          # full / strategy / shortform
    },
    "박팀장": {
        "title": "팀장", "emoji": "🐯",
        "color": "#F57935", "bg": "#FFF1E8",
        "desc": "실행 총괄 · 팀 조율",
        "access": "full",
    },
    "이과장": {
        "title": "과장", "emoji": "🦊",
        "color": "#7C5CFF", "bg": "#F1ECFF",
        "desc": "퍼포먼스 마케팅 · 인플루언서",
        "access": "strategy",
    },
    "김대리": {
        "title": "대리", "emoji": "🐰",
        "color": "#17A976", "bg": "#E9FFF6",
        "desc": "브랜드 리서치 · 숏폼 콘텐츠",
        "access": "shortform",
    },
}

# ══════════════════════════════════════════════════════════════
# REDIRECT IF ALREADY LOGGED IN
# ══════════════════════════════════════════════════════════════
if st.session_state.get("logged_in_user"):
    st.switch_page("pages/1_dashboard.py")

# ══════════════════════════════════════════════════════════════
# LOGIN UI
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="login-root"><div class="login-card">', unsafe_allow_html=True)

st.markdown("""
<div class="login-logo">
    <div class="login-wordmark">에이블</div>
    <div class="login-sub">Z세대 리브랜딩 전략 AI 비서</div>
</div>
<div class="login-label">담당자를 선택해 시작하세요</div>
""", unsafe_allow_html=True)

for name, meta in ROLES.items():
    if st.button(
        f"{meta['emoji']}  {name}  ·  {meta['title']} — {meta['desc']}",
        key=f"login_{name}",
        use_container_width=True,
    ):
        st.session_state["logged_in_user"] = name
        st.session_state["role_meta"] = meta
        st.session_state["ROLES"] = ROLES
        if "tasks" not in st.session_state:
            st.session_state["tasks"] = []
        st.switch_page("pages/1_dashboard.py")

st.markdown("""
<div class="login-footer">ABLE v6 · Anthropic Claude Powered</div>
</div></div>
""", unsafe_allow_html=True)
