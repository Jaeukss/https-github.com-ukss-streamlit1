import os
import requests
import streamlit as st
from openai import OpenAI

# -----------------------------
# 사용자 계정
# -----------------------------
USERS = {
    "김대리": "1234",
    "박대리": "1234",
    "이과장": "1234"
}

def login_ui():
    st.title("로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        if username in USERS and USERS[username] == password:
            st.session_state["user"] = username
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호 오류")

def logout():
    st.session_state.pop("user", None)
    st.rerun()

def user_key(key: str):
    return f"{key}_{st.session_state['user']}"

# -----------------------------
# 로그인 체크
# -----------------------------
if "user" not in st.session_state:
    login_ui()
    st.stop()

# -----------------------------
# 기존 코드 시작
# -----------------------------
st.set_page_config(
    page_title="에이블 | Z세대 리브랜딩 전략 AI 비서",
    page_icon="🧠",
    layout="wide"
)

# 사용자 표시
col_user_1, col_user_2 = st.columns([8, 2])
with col_user_1:
    st.write(f"현재 사용자: {st.session_state['user']}")
with col_user_2:
    if st.button("로그아웃"):
        logout()

st.caption("APP VERSION: able-colab-streamlit-v2-login")

DEFAULT_EMAIL_ADDRESS = "mememeco8@gmail.com"


def get_secret_or_env(key: str, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)


OPENAI_API_KEY = get_secret_or_env("OPENAI_API_KEY")
SENDGRID_API_KEY = get_secret_or_env("SENDGRID_API_KEY")
EMAIL_ADDRESS = get_secret_or_env("EMAIL_ADDRESS", DEFAULT_EMAIL_ADDRESS)

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY가 없습니다.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# (중략: 기존 함수들 그대로 유지)
# -----------------------------
# ask_ai, summarize_meeting, extract_tasks ...
# 그대로 둬라 (변경 없음)

# -----------------------------
# RESULT_KEYS 수정
# -----------------------------
RESULT_KEYS = [
    "summary_result",
    "tasks_result",
    "branding_result",
    "shortform_result",
    "action_risk_result",
    "decisions_result",
    "qa_result",
    "email_draft_result"
]

def clear_results():
    for key in RESULT_KEYS:
        st.session_state.pop(user_key(key), None)

def build_report_text(include_email=True) -> str:
    report = ""

    sections = [
        ("# 1. 회의 핵심 요약", "summary_result"),
        ("# 2. 담당자별 리서치 과제", "tasks_result"),
        ("# 3. 리브랜딩 인사이트", "branding_result"),
        ("# 4. 숏폼 확산 전략", "shortform_result"),
        ("# 5. 실행 계획 및 리스크", "action_risk_result"),
        ("# 6. 전략 결정사항", "decisions_result"),
        ("# 7. 에이블 질의응답", "qa_result"),
    ]

    for title, key in sections:
        ukey = user_key(key)
        if ukey in st.session_state:
            report += title + "\n\n"
            report += st.session_state[ukey] + "\n\n"

    if include_email:
        ukey = user_key("email_draft_result")
        if ukey in st.session_state:
            report += "# 8. 이메일 초안\n\n"
            report += st.session_state[ukey] + "\n\n"

    return report

def run_all_analysis(meeting1_text):
    st.session_state[user_key("summary_result")] = summarize_meeting(meeting1_text)
    st.session_state[user_key("tasks_result")] = extract_tasks(meeting1_text)
    st.session_state[user_key("branding_result")] = branding_insight(meeting1_text)
    st.session_state[user_key("shortform_result")] = shortform_strategy(meeting1_text)
    st.session_state[user_key("action_risk_result")] = action_and_risk(meeting1_text)
    st.session_state[user_key("decisions_result")] = decisions(meeting1_text)

def make_email_draft(meeting1_text, recipient_name, sender_name):
    previous_results = build_report_text(include_email=False)

    return ask_ai(
        "이메일 브리핑 초안 작성",
        f"""
[회의록]
{meeting1_text}

[기존 분석 결과]
{previous_results}

[수신자]
{recipient_name}

[발신자]
{sender_name}
""",
        "이메일 작성"
    )

# -----------------------------
# meeting_text 사용자별 분리
# -----------------------------
if user_key("meeting1_text") not in st.session_state:
    st.session_state[user_key("meeting1_text")] = DEFAULT_MEETING1_TEXT

meeting1_text = st.text_area(
    "meeting1_text",
    key=user_key("meeting1_text"),
    height=300
)

# -----------------------------
# 실행 버튼
# -----------------------------
col_action_1, col_action_2 = st.columns([1, 1])

with col_action_1:
    if st.button("전체 분석 실행"):
        run_all_analysis(meeting1_text)

with col_action_2:
    if st.button("초기화"):
        clear_results()
        st.rerun()

# -----------------------------
# 결과 출력 (핵심 변경)
# -----------------------------
st.subheader("회의 요약")
if user_key("summary_result") in st.session_state:
    st.markdown(st.session_state[user_key("summary_result")])

st.subheader("과제")
if user_key("tasks_result") in st.session_state:
    st.markdown(st.session_state[user_key("tasks_result")])
