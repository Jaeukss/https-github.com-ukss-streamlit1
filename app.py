import os
import requests
import streamlit as st
from openai import OpenAI

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="에이블 | Z세대 리브랜딩 전략 AI 비서",
    page_icon="🧠",
    layout="wide"
)
st.caption("APP VERSION: able-colab-streamlit-v3")

# ══════════════════════════════════════════════════════════════
# PREMIUM CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Fredoka+One&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }

/* ── 전체 배경: 따뜻한 크림 ── */
.stApp {
    background: #FFF8F0;
    color: #3d2f2f;
}
.main .block-container { padding-top: 1.5rem; max-width: 980px; }

/* ── 제목 ── */
h1 {
    font-family: 'Fredoka One', cursive !important;
    font-size: 2.6rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.01em !important;
    background: linear-gradient(90deg, #FF6B9D 0%, #A78BFA 55%, #60C8F5 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 0.1rem !important;
}
h2, h3 {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    color: #3d2f2f !important;
}

/* ── 사이드바: 라벤더 파스텔 ── */
section[data-testid="stSidebar"] {
    background: #F3EEFF !important;
    border-right: 2px solid #DDD0FF !important;
}
section[data-testid="stSidebar"] * { color: #3d2f2f !important; }

/* ── 버튼 ── */
.stButton > button {
    background: #ffffff !important;
    color: #7C3AED !important;
    border: 2px solid #DDD0FF !important;
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    transition: all 0.18s ease !important;
    padding: 0.5rem 1.1rem !important;
}
.stButton > button:hover {
    background: #F3EEFF !important;
    border-color: #A78BFA !important;
    color: #5B21B6 !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 4px 14px rgba(167,139,250,0.25) !important;
}

/* ── 입력창 ── */
textarea, input[type="text"] {
    background: #ffffff !important;
    color: #3d2f2f !important;
    border: 2px solid #DDD0FF !important;
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.95rem !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: #A78BFA !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.18) !important;
}

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFE8F5 !important;
    border-radius: 16px !important;
    gap: 3px !important;
    padding: 5px !important;
    border: 2px solid #FFCCE8 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #C084A8 !important;
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    transition: all 0.18s !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #FF6B9D !important;
    border-bottom: 3px solid #FF6B9D !important;
    box-shadow: 0 2px 8px rgba(255,107,157,0.15) !important;
}

/* ── 구분선 ── */
hr { border-color: #FFDDF0 !important; }

/* ── 익스팬더 ── */
details summary { color: #C084A8 !important; font-size: 0.88rem !important; font-weight: 700 !important; }

/* ════ 로그인 화면 ════ */
.login-wrapper {
    display: flex; flex-direction: column; align-items: center;
    padding: 2.5rem 0 1.5rem;
}
.login-mascot {
    font-size: 5rem;
    margin-bottom: 0.5rem;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-10px); }
}
.login-hero-title {
    font-family: 'Fredoka One', cursive;
    font-size: 3.2rem;
    font-weight: 400;
    background: linear-gradient(90deg, #FF6B9D 0%, #A78BFA 55%, #60C8F5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    line-height: 1.1;
}
.login-hero-sub {
    color: #C084A8;
    font-size: 0.92rem;
    font-weight: 600;
    text-align: center;
    margin-top: 0.4rem;
    margin-bottom: 2rem;
}
.role-card {
    background: #ffffff;
    border: 2.5px solid #F0E0FF;
    border-radius: 20px;
    padding: 1rem 1.4rem;
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 10px;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(167,139,250,0.08);
}
.role-card:hover {
    transform: translateY(-3px) scale(1.01);
    box-shadow: 0 8px 24px rgba(167,139,250,0.18);
}
.role-card .r-name {
    font-family: 'Nunito', sans-serif;
    font-size: 1.05rem;
    font-weight: 800;
    color: #3d2f2f;
}
.role-card .r-desc { font-size: 0.75rem; margin-top: 2px; font-weight: 600; }
.role-avatar {
    width: 52px; height: 52px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.7rem; flex-shrink: 0;
}
.r-arrow { margin-left: auto; font-size: 1.2rem; opacity: 0.5; }

/* ════ 사이드바 배지 ════ */
.user-badge {
    border-radius: 18px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    text-align: center;
}
.badge-mascot { font-size: 2.8rem; margin-bottom: 4px; }
.badge-role {
    font-size: 0.68rem; font-weight: 800;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px;
}
.badge-name {
    font-family: 'Fredoka One', cursive;
    font-size: 1.3rem; font-weight: 400; color: #3d2f2f !important;
}
.badge-desc { font-size: 0.74rem; font-weight: 600; margin-top: 3px; }

.sidebar-menu-label {
    font-size: 0.68rem; font-weight: 800; letter-spacing: 0.1em;
    text-transform: uppercase; color: #C084A8 !important;
    margin: 12px 0 6px;
}
.sidebar-menu-item {
    font-size: 0.84rem; font-weight: 700; padding: 5px 8px;
    border-radius: 10px; margin-bottom: 3px; color: #5d3f6a !important;
    transition: background 0.15s;
}
.sidebar-menu-item:hover { background: #EDD9FF; }

/* ════ 접근 불가 ════ */
.access-denied {
    background: linear-gradient(135deg, #FFF0FA, #F0EEFF);
    border: 2px dashed #DDB9FF;
    border-radius: 20px;
    padding: 3rem 2rem;
    text-align: center;
    margin-top: 1rem;
}
.access-denied .ad-mascot { font-size: 3rem; margin-bottom: 0.5rem; }
.access-denied .ad-title { color: #9B59F7; font-size: 1.1rem; font-weight: 800; }
.access-denied .ad-sub { color: #B89CC8; margin-top: 0.5rem; font-size: 0.88rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ROLE DEFINITIONS
# ══════════════════════════════════════════════════════════════
ROLES = {
    "김부장": {
        "title": "부장",
        "color": "#4F8EF7",
        "pastel_bg": "#EBF3FF",
        "mascot": "🦁",
        "description": "전략 총괄 · 최종 결재",
        "allowed_tabs": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "박팀장": {
        "title": "팀장",
        "color": "#FF8C69",
        "pastel_bg": "#FFF0EB",
        "mascot": "🐯",
        "description": "실행 총괄 · 팀 조율",
        "allowed_tabs": [0, 1, 2, 3, 4, 5, 6, 7],
    },
    "이과장": {
        "title": "과장",
        "color": "#A78BFA",
        "pastel_bg": "#F3EEFF",
        "mascot": "🦊",
        "description": "퍼포먼스 마케팅 · 인플루언서",
        "allowed_tabs": [0, 1, 4, 6],
    },
    "김대리": {
        "title": "대리",
        "color": "#34C98E",
        "pastel_bg": "#E8FBF4",
        "mascot": "🐰",
        "description": "브랜드 리서치 · 숏폼 콘텐츠",
        "allowed_tabs": [0, 1, 2, 3, 6],
    },
}

TAB_LABELS = [
    ("📋", "회의 요약"),
    ("✅", "담당자별 과제"),
    ("💡", "리브랜딩 인사이트"),
    ("🎬", "숏폼 전략"),
    ("⚙️", "실행 계획·리스크"),
    ("🔒", "결정사항"),
    ("🤖", "에이블 Q&A"),
    ("📧", "이메일 발송"),
]

# ══════════════════════════════════════════════════════════════
# SECRETS / ENV
# ══════════════════════════════════════════════════════════════
DEFAULT_EMAIL_ADDRESS = "mememeco8@gmail.com"

def get_secret_or_env(key: str, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

OPENAI_API_KEY   = get_secret_or_env("OPENAI_API_KEY")
SENDGRID_API_KEY = get_secret_or_env("SENDGRID_API_KEY")
EMAIL_ADDRESS    = get_secret_or_env("EMAIL_ADDRESS", DEFAULT_EMAIL_ADDRESS)

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY가 없습니다.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ══════════════════════════════════════════════════════════════
# PROJECT CONTEXT
# ══════════════════════════════════════════════════════════════
PROJECT_CONTEXT = """
[프로젝트 배경 및 문제 정의]
1. 핵심 과제: 전통의 현대화 - Z세대 타겟 리브랜딩 및 숏폼 확산 전략
20년 된 장수 브랜드의 '아빠 브랜드' 이미지를 탈피하기 위해, 브랜드 정체성을 재정립함과 동시에
저예산 고효율 매체인 숏폼을 활용하여 Z세대에게 브랜드 인지도를 확산시키는 것을 목표로 한다.

2. 현재 상황 및 당면 문제
브랜드 위기: 장수 브랜드로서의 신뢰도는 높으나, 1020 세대와의 접점이 없어 신규 유입이 단절됨.
자원 한계: 대규모 TV CF 등 전통적 광고 예산은 제한적임. 아이디어 고갈로 디지털 트렌드 대응력이 낮아진 상태.
전략적 공백: Z세대가 좋아하는 톤앤매너와 구매로 이어지는 숏폼 마케팅 공식에 대한 데이터가 부족함.

3. 주요 수행 업무
Part 1. 브랜드 이미지 쇄신 로직 - 글로벌 성공 사례 분석 / Z세대 커뮤니케이션 방식, 팝업스토어 트렌드 조사
Part 2. 디지털 확산 및 전환 전략 - 숏폼 성공 공식 도출 / 인플루언서 협업 성공 사례 리서치
"""

DEFAULT_MEETING1_TEXT = """
오늘 회의에서는 20년 된 장수 브랜드의 Z세대 리브랜딩 방향을 논의했다.
현재 브랜드는 신뢰도는 높지만 1020 세대에게는 아빠 브랜드 이미지가 강하다는 점이 문제로 제기되었다.
김 대리는 올드스파이스와 구찌의 리브랜딩 사례를 조사하기로 했다.
박 대리는 최근 3개월간 틱톡과 릴스에서 바이럴된 챌린지 사례를 정리하기로 했다.
이 과장은 인플루언서 협업을 통한 구매 전환 사례를 조사하기로 했다.
팀에서는 대규모 TV 광고보다 숏폼 중심의 저예산 확산 전략이 필요하다고 판단했다.
다만 브랜드 정체성을 훼손하지 않으면서 Z세대에게 어색하지 않은 톤앤매너를 찾는 것이 중요하다는 의견이 있었다.
다음 회의 전까지 각자 조사한 내용을 공유하고, 숏폼 챌린지 아이디어를 3개 이상 제안하기로 했다.
"""

# ══════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ══════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <div class="login-wrapper">
        <div class="login-mascot">🧠✨</div>
        <div class="login-hero-title">에이블</div>
        <div class="login-hero-sub">Z세대 리브랜딩 전략 AI 비서 · 담당자를 선택해주세요 🎯</div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        for name, meta in ROLES.items():
            color      = meta["color"]
            pastel_bg  = meta["pastel_bg"]
            mascot     = meta["mascot"]
            st.markdown(f"""
            <div class="role-card" style="border-color:{color}55;">
                <div class="role-avatar" style="background:{pastel_bg}; font-size:1.9rem;">
                    {mascot}
                </div>
                <div>
                    <div class="r-name">{name}</div>
                    <div class="r-desc" style="color:{color};">{meta['title']} · {meta['description']}</div>
                </div>
                <div class="r-arrow" style="color:{color};">→</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"{mascot}  {name} 으로 시작하기", key=f"login_{name}", use_container_width=True):
                st.session_state["logged_in_user"] = name
                st.rerun()

# ══════════════════════════════════════════════════════════════
# SIDEBAR BADGE
# ══════════════════════════════════════════════════════════════
def render_sidebar():
    user = st.session_state.get("logged_in_user")
    if not user:
        return
    meta       = ROLES[user]
    color      = meta["color"]
    pastel_bg  = meta["pastel_bg"]
    mascot     = meta["mascot"]

    with st.sidebar:
        st.markdown(f"""
        <div class="user-badge" style="background:{pastel_bg}; border:2px solid {color}44;">
            <div class="badge-mascot">{mascot}</div>
            <div class="badge-role" style="color:{color};">접속 중</div>
            <div class="badge-name">{user}</div>
            <div class="badge-desc" style="color:{color};">{meta['title']} · {meta['description']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("👋  로그아웃", use_container_width=True):
            st.session_state.pop("logged_in_user", None)
            st.rerun()

        st.markdown("<div class='sidebar-menu-label'>접근 가능 메뉴</div>", unsafe_allow_html=True)
        for i in meta["allowed_tabs"]:
            icon, label = TAB_LABELS[i]
            st.markdown(
                f"<div class='sidebar-menu-item'>"
                f"<span style='margin-right:6px;'>{icon}</span>{label}</div>",
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════
# ACCESS GUARD
# ══════════════════════════════════════════════════════════════
def can_access(tab_index: int) -> bool:
    user = st.session_state.get("logged_in_user")
    if not user or user not in ROLES:
        return False
    return tab_index in ROLES[user]["allowed_tabs"]

def show_access_denied(tab_index: int):
    _, label = TAB_LABELS[tab_index]
    st.markdown(f"""
    <div class="access-denied">
        <div class="ad-mascot">🔒🙈</div>
        <div class="ad-title">{label} 메뉴는 열쇠가 필요해요!</div>
        <div class="ad-sub">현재 계정의 접근 권한이 없는 메뉴입니다.<br>담당자에게 문의해주세요 🌸</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# AI HELPERS  (기존 함수 동일)
# ══════════════════════════════════════════════════════════════
def ask_ai(task_title, user_input, output_instruction):
    if not user_input or not user_input.strip():
        return "입력 내용이 없습니다."
    prompt = f"""
너는 AI 비서 '에이블'이다. 아래 프로젝트 배경을 반영하라.
{PROJECT_CONTEXT}

[분석 목적] {task_title}
[사용자 입력] {user_input}
[출력 지시] {output_instruction}

[공통 규칙]
- 한국어로 작성
- 입력에 없는 사실은 추측하지 말 것
- 불확실한 정보는 "입력 내용에서 확인 불가"라고 표시
- 표가 적합하면 Markdown 표로 작성
- Z세대 리브랜딩과 숏폼 확산 전략 관점에서 해석
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 Z세대 리브랜딩과 숏폼 확산 전략을 지원하는 AI 비서 에이블이다."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2
    )
    return resp.choices[0].message.content

def summarize_meeting(t):
    return ask_ai("회의 핵심 요약", t,
        "1.회의 목적 2.핵심 논의 3.리브랜딩 논의 4.숏폼 논의 5.확정 사항 6.미해결 7.다음 회의 확인 항목")

def extract_tasks(t):
    return ask_ai("담당자별 과제 추출", t,
        "| 담당자 | 업무 | 관련 파트 | 마감일 | 우선순위 | 근거 | 형식의 Markdown 표로 정리")

def branding_insight(t):
    return ask_ai("리브랜딩 인사이트", t,
        "1.기존 이미지 문제 2.새 이미지 방향 3.유지할 자산 4.버릴 이미지 5.글로벌 사례 방향 6.팝업 아이디어 7.톤앤매너")

def shortform_strategy(t):
    return ask_ai("숏폼 확산 전략", t,
        "1.핵심 메시지 2.톤앤매너 3.챌린지/밈 4.플랫폼별 방향 5.인플루언서 협업 6.구매 전환 장치 7.저예산 실험안")

def action_and_risk(t):
    return ask_ai("실행 계획 및 리스크", t,
        "실행 계획 표 (번호|실행항목|담당자|마감일|우선순위|산출물) + 리스크 표 (번호|유형|내용|영향|대응)")

def decisions(t):
    return ask_ai("결정사항 추출", t,
        "| 번호 | 결정사항 | 관련 영역 | 결정 배경 | 후속 조치 | 근거 | 형식의 표만 작성")

def ask_able(question, reference_text):
    return ask_ai("에이블 Q&A", f"[참고]\n{reference_text}\n\n[질문]\n{question}",
        "1.핵심 답변 2.근거 3.리브랜딩 시사점 4.숏폼 시사점 5.즉시 실행 액션")

def send_email(to, subject, body):
    if not SENDGRID_API_KEY:
        return {"status": "failed", "error": "SENDGRID_API_KEY 없음"}
    if not to or "@" not in to:
        return {"status": "failed", "error": "이메일 주소 오류"}
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
    data = {
        "personalizations": [{"to": [{"email": to}], "subject": subject}],
        "from": {"email": EMAIL_ADDRESS},
        "content": [{"type": "text/plain", "value": body}]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        return {"status": "success"} if r.status_code == 202 else {"status": "failed", "error": r.text}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# ── result key helpers ──
RESULT_KEYS = ["summary_result","tasks_result","branding_result","shortform_result",
               "action_risk_result","decisions_result","qa_result","email_draft_result"]

def clear_results():
    for k in RESULT_KEYS:
        st.session_state.pop(k, None)

def build_report_text(include_email=True):
    sections = [
        ("# 1. 회의 핵심 요약",      "summary_result"),
        ("# 2. 담당자별 과제",        "tasks_result"),
        ("# 3. 리브랜딩 인사이트",    "branding_result"),
        ("# 4. 숏폼 확산 전략",       "shortform_result"),
        ("# 5. 실행 계획 및 리스크",  "action_risk_result"),
        ("# 6. 전략 결정사항",        "decisions_result"),
        ("# 7. 에이블 Q&A",           "qa_result"),
    ]
    report = ""
    for title, key in sections:
        if key in st.session_state:
            report += title + "\n\n" + st.session_state[key] + "\n\n"
    if include_email and "email_draft_result" in st.session_state:
        report += "# 8. 이메일 초안\n\n" + st.session_state["email_draft_result"] + "\n\n"
    return report

def run_all_analysis(t):
    st.session_state["summary_result"]     = summarize_meeting(t)
    st.session_state["tasks_result"]       = extract_tasks(t)
    st.session_state["branding_result"]    = branding_insight(t)
    st.session_state["shortform_result"]   = shortform_strategy(t)
    st.session_state["action_risk_result"] = action_and_risk(t)
    st.session_state["decisions_result"]   = decisions(t)

def make_email_draft(t, recipient_name, sender_name):
    prev = build_report_text(include_email=False)
    return ask_ai("이메일 초안",
        f"[회의록]\n{t}\n\n[분석 결과]\n{prev}\n\n[수신자] {recipient_name} / [발신자] {sender_name}",
        "업무 이메일 톤으로 회의 핵심·담당자 업무·리브랜딩·숏폼·실행 계획 포함한 브리핑 작성. 제목 포함.")

# ══════════════════════════════════════════════════════════════
# LOGIN GATE
# ══════════════════════════════════════════════════════════════
if "logged_in_user" not in st.session_state:
    show_login()
    st.stop()

render_sidebar()

# ══════════════════════════════════════════════════════════════
# MAIN HEADER
# ══════════════════════════════════════════════════════════════
user      = st.session_state["logged_in_user"]
user_meta = ROLES[user]
color     = user_meta["color"]

st.title("에이블 ✨")
st.markdown(
    f"<span style='color:{color};font-size:0.9rem;font-weight:700;'>"
    f"{user_meta['mascot']} {user} ({user_meta['title']})</span>"
    f"<span style='color:#C084A8;font-size:0.9rem;font-weight:600;'> · Z세대 리브랜딩 전략 AI 비서 🎯</span>",
    unsafe_allow_html=True
)

with st.expander("프로젝트 배경 보기"):
    st.markdown(PROJECT_CONTEXT)

with st.expander("시스템 설정 확인"):
    st.write("OpenAI API Key:", bool(OPENAI_API_KEY))
    st.write("SendGrid API Key:", bool(SENDGRID_API_KEY))
    st.write("발신자:", EMAIL_ADDRESS)

# ══════════════════════════════════════════════════════════════
# MEETING INPUT
# ══════════════════════════════════════════════════════════════
if "meeting1_text" not in st.session_state:
    st.session_state["meeting1_text"] = DEFAULT_MEETING1_TEXT

uploaded_file = st.file_uploader("회의록 파일 업로드", type=["txt", "md"])
if uploaded_file is not None:
    uploaded_text = uploaded_file.read().decode("utf-8")
    if st.session_state.get("last_uploaded_file") != uploaded_file.name:
        st.session_state["meeting1_text"] = uploaded_text
        st.session_state["last_uploaded_file"] = uploaded_file.name
        clear_results()
        st.rerun()

c1, c2 = st.columns(2)
with c1:
    if st.button("예시 회의록 불러오기", use_container_width=True):
        st.session_state["meeting1_text"] = DEFAULT_MEETING1_TEXT
        clear_results()
        st.rerun()
with c2:
    if st.button("입력창 비우기", use_container_width=True):
        st.session_state["meeting1_text"] = ""
        clear_results()
        st.rerun()

meeting1_text = st.text_area(
    "회의록",
    key="meeting1_text",
    height=260,
    placeholder="회의록 내용을 입력하세요.",
    label_visibility="collapsed"
)
st.caption(f"글자 수: {len(meeting1_text)}")

ca, cb = st.columns(2)
with ca:
    if st.button("⚡  전체 분석 실행", use_container_width=True):
        with st.spinner("에이블이 분석 중입니다..."):
            run_all_analysis(meeting1_text)
with cb:
    if st.button("↺  분석 초기화", use_container_width=True):
        clear_results()
        st.rerun()

st.divider()

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab_labels = [f"{icon} {label}" for icon, label in TAB_LABELS]
tabs = st.tabs(tab_labels)

# ── Tab 0: 회의 요약 ──
with tabs[0]:
    if not can_access(0):
        show_access_denied(0)
    else:
        st.subheader("📋 회의 핵심 요약")
        if st.button("요약 생성", key="btn_summary"):
            with st.spinner("생성 중..."):
                st.session_state["summary_result"] = summarize_meeting(meeting1_text)
        if "summary_result" in st.session_state:
            st.markdown(st.session_state["summary_result"])
        else:
            st.info("아직 결과가 없습니다.")

# ── Tab 1: 담당자별 과제 ──
with tabs[1]:
    if not can_access(1):
        show_access_denied(1)
    else:
        st.subheader("✅ 담당자별 리서치 과제")
        if st.button("과제 추출", key="btn_tasks"):
            with st.spinner("생성 중..."):
                st.session_state["tasks_result"] = extract_tasks(meeting1_text)
        if "tasks_result" in st.session_state:
            st.markdown(st.session_state["tasks_result"])
        else:
            st.info("아직 결과가 없습니다.")

# ── Tab 2: 리브랜딩 인사이트 ──
with tabs[2]:
    if not can_access(2):
        show_access_denied(2)
    else:
        st.subheader("💡 리브랜딩 인사이트")
        if st.button("인사이트 생성", key="btn_branding"):
            with st.spinner("생성 중..."):
                st.session_state["branding_result"] = branding_insight(meeting1_text)
        if "branding_result" in st.session_state:
            st.markdown(st.session_state["branding_result"])
        else:
            st.info("아직 결과가 없습니다.")

# ── Tab 3: 숏폼 전략 ──
with tabs[3]:
    if not can_access(3):
        show_access_denied(3)
    else:
        st.subheader("🎬 숏폼 확산 전략")
        if st.button("전략 생성", key="btn_shortform"):
            with st.spinner("생성 중..."):
                st.session_state["shortform_result"] = shortform_strategy(meeting1_text)
        if "shortform_result" in st.session_state:
            st.markdown(st.session_state["shortform_result"])
        else:
            st.info("아직 결과가 없습니다.")

# ── Tab 4: 실행 계획·리스크 ──
with tabs[4]:
    if not can_access(4):
        show_access_denied(4)
    else:
        st.subheader("⚙️ 실행 계획 및 리스크")
        if st.button("생성", key="btn_action"):
            with st.spinner("생성 중..."):
                st.session_state["action_risk_result"] = action_and_risk(meeting1_text)
        if "action_risk_result" in st.session_state:
            st.markdown(st.session_state["action_risk_result"])
        else:
            st.info("아직 결과가 없습니다.")

# ── Tab 5: 결정사항 ──
with tabs[5]:
    if not can_access(5):
        show_access_denied(5)
    else:
        st.subheader("🔒 전략 결정사항")
        if st.button("추출", key="btn_decisions"):
            with st.spinner("생성 중..."):
                st.session_state["decisions_result"] = decisions(meeting1_text)
        if "decisions_result" in st.session_state:
            st.markdown(st.session_state["decisions_result"])
        else:
            st.info("아직 결과가 없습니다.")

# ── Tab 6: Q&A ──
with tabs[6]:
    if not can_access(6):
        show_access_denied(6)
    else:
        st.subheader("🤖 에이블 Q&A")
        question = st.text_input(
            "질문",
            value="리브랜딩을 위해 참고할 만한 글로벌 사례와 숏폼 챌린지 성공 공식은?",
            label_visibility="collapsed",
            placeholder="에이블에게 질문하기"
        )
        if st.button("질문하기", key="btn_qa"):
            with st.spinner("답변 생성 중..."):
                st.session_state["qa_result"] = ask_able(
                    question=question,
                    reference_text=meeting1_text + "\n\n" + build_report_text(include_email=False)
                )
        if "qa_result" in st.session_state:
            st.markdown(st.session_state["qa_result"])
        else:
            st.info("아직 결과가 없습니다.")

# ── Tab 7: 이메일 ──
with tabs[7]:
    if not can_access(7):
        show_access_denied(7)
    else:
        st.subheader("📧 이메일 초안 생성 및 발송")
        recipient_name  = st.text_input("수신자명",   value="팀장님")
        recipient_email = st.text_input("수신자 이메일", value="")
        sender_name     = st.text_input("발신자명",   value="에이블")
        email_subject   = st.text_input("이메일 제목",
            value="[에이블 브리핑] Z세대 리브랜딩 및 숏폼 확산 전략 회의 정리")

        if st.button("이메일 초안 생성", key="btn_email"):
            with st.spinner("초안 생성 중..."):
                st.session_state["email_draft_result"] = make_email_draft(
                    meeting1_text, recipient_name, sender_name
                )

        if "email_draft_result" in st.session_state:
            email_body = st.text_area("이메일 본문",
                value=st.session_state["email_draft_result"], height=400)
            ec1, ec2 = st.columns(2)
            with ec1:
                st.download_button("⬇ 초안 TXT 다운로드", data=email_body,
                    file_name="able_email_draft.txt", mime="text/plain", use_container_width=True)
            with ec2:
                if st.button("SendGrid 발송", use_container_width=True):
                    with st.spinner("발송 중..."):
                        result = send_email(recipient_email, email_subject, email_body)
                    if result["status"] == "success":
                        st.success("발송 완료")
                    else:
                        st.error("발송 실패")
                        st.json(result)
        else:
            st.info("아직 이메일 초안이 없습니다.")

# ══════════════════════════════════════════════════════════════
# DOWNLOAD ALL
# ══════════════════════════════════════════════════════════════
st.divider()
st.subheader("전체 결과 다운로드")
final_report = build_report_text()
if final_report.strip():
    st.download_button(
        "⬇ 전체 분석 결과 Markdown 다운로드",
        data=final_report,
        file_name="able_project_report.md",
        mime="text/markdown",
        use_container_width=True
    )
else:
    st.info("다운로드할 분석 결과가 없습니다.")
