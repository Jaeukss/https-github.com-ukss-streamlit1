# -*- coding: utf-8 -*-
import os
import streamlit as st

st.set_page_config(
    page_title="에이블 | Z세대 리브랜딩 AI 비서",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = os.path.dirname(__file__)
ABLE_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "able_bunny.png")

# ══════════════════════════════════════════════════════════════
# GLOBAL STYLE - LOGIN ONLY
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Pretendard:wght@300;400;500;600;700&display=swap');

/* Login에서는 기본 Streamlit UI 숨김 */
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; height: 0 !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton { display: none !important; }
[data-testid="stHeader"] { height: 0 !important; background: transparent !important; }

html, body, [class*="css"] {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif !important;
}
.stApp, [data-testid="stAppViewContainer"] {
    background: #F7F4FF !important;
}
.block-container {
    padding-top: 0.15rem !important;
    padding-bottom: 0 !important;
    max-width: 1120px !important;
}

/* ── COMPACT LOGIN LAYOUT ── */
.login-shell {
    min-height: calc(100vh - 12px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.35rem 0.6rem;
}
.login-panel {
    width: 100%;
    max-width: 980px;
    background: rgba(255,255,255,0.66);
    border: 1px solid #E5DDF7;
    border-radius: 28px;
    box-shadow: 0 18px 50px rgba(124,92,255,0.10);
    padding: 1rem 1.1rem;
}
.login-grid {
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 1.25rem;
    align-items: center;
}
.login-mascot-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 380px;
}
.login-mascot-card {
    width: 100%;
    max-width: 360px;
    aspect-ratio: 1 / 1;
    background: linear-gradient(145deg, #FFFFFF 0%, #F1ECFF 100%);
    border: 1px solid #E5DDF7;
    border-radius: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.login-mascot-card img {
    width: 92%;
    height: 92%;
    object-fit: contain;
}
.login-card {
    width: 100%;
    max-width: 460px;
    margin: 0 auto;
}
.login-logo {
    text-align: left;
    margin-bottom: 0.65rem;
}
.login-wordmark {
    font-family: 'Syne', sans-serif;
    font-size: 2.35rem;
    font-weight: 800;
    background: linear-gradient(120deg, #7C5CFF 0%, #E94C98 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.035em;
    line-height: 0.95;
}
.login-sub {
    font-size: 0.78rem;
    color: #766D8A;
    margin-top: 0.28rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.login-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #6F6682;
    margin: 0.7rem 0 0.42rem;
}

/* 버튼을 작고 균형 있게 */
.stButton > button {
    background: #FFFFFF !important;
    border: 1px solid #DDD3F2 !important;
    border-radius: 14px !important;
    color: #2E2940 !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 0.86rem !important;
    font-weight: 650 !important;
    padding: 0.56rem 0.85rem !important;
    min-height: 42px !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.16s !important;
    margin-bottom: 0.22rem !important;
    box-shadow: 0 4px 12px rgba(124,92,255,0.04) !important;
}
.stButton > button:hover {
    background: #F2ECFF !important;
    border-color: #B49DFF !important;
    transform: translateY(-1px) !important;
}
.login-footer {
    text-align: left;
    margin-top: 0.55rem;
    font-size: 0.68rem;
    color: #9B92AD;
    letter-spacing: 0.04em;
}

@media (max-height: 760px) {
    .login-panel { padding: 0.7rem 0.9rem; border-radius: 22px; }
    .login-mascot-wrap { min-height: 310px; }
    .login-mascot-card { max-width: 300px; border-radius: 24px; }
    .login-wordmark { font-size: 2.05rem; }
    .login-sub { font-size: 0.72rem; }
    .login-label { margin-top: 0.55rem; }
    .stButton > button { min-height: 38px !important; padding: 0.45rem 0.75rem !important; font-size: 0.82rem !important; }
}
@media (max-width: 820px) {
    .login-shell { align-items: flex-start; padding-top: 0.4rem; }
    .login-grid { grid-template-columns: 1fr; gap: 0.55rem; }
    .login-mascot-wrap { min-height: auto; }
    .login-mascot-card { max-width: 170px; max-height: 170px; }
    .login-card { max-width: 460px; }
    .login-logo, .login-footer { text-align: center; }
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
        "access": "full",
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
        "access": "full",
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
def do_login(name: str, meta: dict):
    st.session_state["logged_in_user"] = name
    st.session_state["role_meta"] = meta
    st.session_state["ROLES"] = ROLES
    if "tasks" not in st.session_state:
        st.session_state["tasks"] = []
    st.switch_page("pages/1_dashboard.py")

image_html = ""
if os.path.exists(ABLE_IMAGE_PATH):
    import base64
    with open(ABLE_IMAGE_PATH, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
    image_html = f'<img src="data:image/png;base64,{image_b64}" alt="에이블 캐릭터" />'
else:
    image_html = '<div style="font-size:5rem;">🐰</div>'

st.markdown(f"""
<div class="login-shell">
  <div class="login-panel">
    <div class="login-grid">
      <div class="login-mascot-wrap">
        <div class="login-mascot-card">{image_html}</div>
      </div>
      <div class="login-card">
        <div class="login-logo">
          <div class="login-wordmark">에이블</div>
          <div class="login-sub">Z세대 리브랜딩 전략 AI 비서</div>
        </div>
        <div class="login-label">담당자를 선택해 시작하세요</div>
""", unsafe_allow_html=True)

# 버튼 키 충돌 방지를 위해 기존 login_* 키를 쓰지 않고, 고유 prefix를 사용합니다.
for idx, (name, meta) in enumerate(ROLES.items(), start=1):
    if st.button(
        f"{meta['emoji']}  {name}  ·  {meta['title']} — {meta['desc']}",
        key=f"role_select_compact_{idx}_{name}",
        use_container_width=True,
    ):
        do_login(name, meta)

st.markdown("""
        <div class="login-footer">ABLE v6 · AI Work Assistant</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
