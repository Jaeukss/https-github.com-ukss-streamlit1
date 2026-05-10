# -*- coding: utf-8 -*-
# shared.py — common constants, CSS, helpers imported by every page

import os
import re
import json
import tempfile
from pathlib import Path
import streamlit as st
from openai import OpenAI

BASE_DIR = os.path.dirname(__file__)
ABLE_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "able_bunny.png")

# ══════════════════════════════════════════════════════════════
# ROLES  (mirrored here so pages can import without app.py)
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
# PROJECT CONTEXT
# ══════════════════════════════════════════════════════════════
PROJECT_CONTEXT = """
[프로젝트 배경]
핵심 과제: 20년 된 장수 브랜드의 '아빠 브랜드' 이미지를 탈피하고 Z세대 리브랜딩 및 숏폼 확산 전략 수립.

당면 문제:
- 1020세대와의 접점 단절 / 신규 유입 없음
- 대규모 광고 예산 제한 → 저예산 고효율 숏폼 전략 필요
- Z세대 톤앤매너 · 숏폼 성공 공식 데이터 부족

수행 업무:
Part 1. 브랜드 이미지 쇄신 — 글로벌 사례 분석, 팝업스토어 트렌드, Z세대 커뮤니케이션 방식 조사
Part 2. 디지털 확산 및 전환 — 숏폼 성공 공식 도출, 인플루언서 협업 사례 리서치
"""

DEFAULT_MEETING_TEXT = """오늘 회의에서는 20년 된 장수 브랜드의 Z세대 리브랜딩 방향을 논의했다.
현재 브랜드는 신뢰도는 높지만 1020 세대에게는 아빠 브랜드 이미지가 강하다는 점이 문제로 제기되었다.
김 대리는 올드스파이스와 구찌의 리브랜딩 사례를 조사하기로 했다.
박 대리는 최근 3개월간 틱톡과 릴스에서 바이럴된 챌린지 사례를 정리하기로 했다.
이 과장은 인플루언서 협업을 통한 구매 전환 사례를 조사하기로 했다.
팀에서는 대규모 TV 광고보다 숏폼 중심의 저예산 확산 전략이 필요하다고 판단했다.
다만 브랜드 정체성을 훼손하지 않으면서 Z세대에게 어색하지 않은 톤앤매너를 찾는 것이 중요하다는 의견이 있었다.
다음 회의 전까지 각자 조사한 내용을 공유하고, 숏폼 챌린지 아이디어를 3개 이상 제안하기로 했다."""

# ══════════════════════════════════════════════════════════════
# SECRETS
# ══════════════════════════════════════════════════════════════
def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

OPENAI_API_KEY   = get_secret("OPENAI_API_KEY")
SENDGRID_API_KEY = get_secret("SENDGRID_API_KEY")
EMAIL_ADDRESS    = "mememeco8@gmail.com"  # SendGrid Verified Sender Identity

def get_openai_client():
    if not OPENAI_API_KEY:
        st.error("⚠️ OPENAI_API_KEY가 설정되지 않았습니다.")
        st.stop()
    return OpenAI(api_key=OPENAI_API_KEY)

# ══════════════════════════════════════════════════════════════
# RESULT KEYS
# ══════════════════════════════════════════════════════════════
RESULT_KEYS = [
    "summary_result", "tasks_result", "branding_result",
    "action_risk_result", "decisions_result", "qa_result",
    "email_draft_result", "notify_result",
    "shortform_result", "script_result", "ab_result",
    "keywords_result", "news_result", "compare_result",
]

def clear_results():
    for k in RESULT_KEYS:
        st.session_state.pop(k, None)


# ══════════════════════════════════════════════════════════════
# AUDIO HELPERS (STT / TTS)
# ══════════════════════════════════════════════════════════════
def transcribe_audio_file(audio_file) -> str:
    """음성 파일을 회의록 텍스트로 변환합니다. st.audio_input 또는 업로드 파일을 받습니다."""
    if audio_file is None:
        return ""
    client = get_openai_client()
    name = getattr(audio_file, "name", "meeting_audio.wav") or "meeting_audio.wav"
    suffix = Path(name).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_file.getvalue())
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="ko",
            )
        return getattr(transcript, "text", "") or ""
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def synthesize_speech(text: str, voice: str = "alloy") -> bytes:
    """분석 결과 텍스트를 음성 파일(mp3 bytes)로 변환합니다."""
    if not text or not str(text).strip():
        return b""
    client = get_openai_client()
    clean_text = str(text).strip()
    # TTS 입력이 너무 길면 실패할 수 있어 앞부분 중심으로 읽습니다.
    if len(clean_text) > 3800:
        clean_text = clean_text[:3800] + "\n\n이후 내용은 화면에서 확인해주세요."
    resp = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=clean_text,
    )
    if hasattr(resp, "content"):
        return resp.content
    return resp.read()


def render_tts_control(text: str, key: str, label: str = "🔊 결과 음성으로 듣기"):
    """결과 영역 하단에 작게 붙이는 TTS 컨트롤입니다."""
    if not text or not str(text).strip():
        return
    with st.expander(label, expanded=False):
        c1, c2 = st.columns([1, 3])
        with c1:
            voice = st.selectbox(
                "음성",
                ["alloy", "nova", "shimmer", "echo", "fable", "onyx"],
                index=1,
                key=f"{key}_voice",
                label_visibility="collapsed",
            )
        with c2:
            if st.button("음성 생성", key=f"{key}_make", use_container_width=True):
                with st.spinner("음성 생성 중…"):
                    st.session_state[f"{key}_audio"] = synthesize_speech(text, voice)
        if st.session_state.get(f"{key}_audio"):
            st.audio(st.session_state[f"{key}_audio"], format="audio/mp3")

# ══════════════════════════════════════════════════════════════
# AI CORE
# ══════════════════════════════════════════════════════════════
LENGTH_PROMPTS = {
    "짧게": "핵심만 3~4줄로 간결하게",
    "보통": "표준 길이로 균형있게",
    "자세히": "각 항목을 상세히 최대한 풍부하게",
}

def ask_ai(task_title: str, user_input: str, output_instruction: str, temperature: float = 0.2) -> str:
    if not user_input or not user_input.strip():
        return "입력 내용이 없습니다."
    client = get_openai_client()
    prompt = (
        f"너는 AI 비서 '에이블'이다. 아래 프로젝트 배경을 반영하라.\n{PROJECT_CONTEXT}"
        f"\n[분석 목적] {task_title}"
        f"\n[사용자 입력] {user_input}"
        f"\n[출력 지시] {output_instruction}"
        "\n\n[공통 규칙]\n- 한국어로 작성\n- 입력에 없는 사실은 추측하지 말 것\n"
        "- 불확실한 정보는 '입력 내용에서 확인 불가'라고 표시\n"
        "- 표가 적합하면 Markdown 표로 작성\n"
        "- Z세대 리브랜딩과 숏폼 확산 전략 관점에서 해석"
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 Z세대 리브랜딩과 숏폼 확산 전략을 지원하는 AI 비서 에이블이다."},
            {"role": "user",   "content": prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content



def build_assistant_context(current_page: str = "") -> str:
    """사이드바 챗봇이 현재 앱 상태를 짧게 참고할 수 있도록 컨텍스트를 구성합니다."""
    meeting_text = st.session_state.get("meeting_text", "")
    context_parts = [PROJECT_CONTEXT]
    if current_page:
        context_parts.append(f"[현재 페이지] {current_page}")
    if meeting_text.strip():
        context_parts.append("[현재 회의록]\n" + meeting_text[:2400])

    result_labels = {
        "summary_result": "회의 요약",
        "tasks_result": "담당자 과제",
        "branding_result": "리브랜딩 인사이트",
        "action_risk_result": "실행·리스크",
        "decisions_result": "결정사항",
        "shortform_result": "숏폼 전략",
        "script_result": "숏폼 스크립트",
        "ab_result": "A/B 테스트",
        "news_result": "관련 뉴스",
    }
    for key, label in result_labels.items():
        val = st.session_state.get(key)
        if val:
            context_parts.append(f"[{label}]\n{str(val)[:1200]}")

    tasks = st.session_state.get("tasks", [])
    if tasks:
        task_lines = []
        for t in tasks[:12]:
            task_lines.append(
                f"- {t.get('title','업무명 없음')} / 담당자:{t.get('assignee','미정')} "
                f"/ 상태:{t.get('status','진행 예정')} / 우선순위:{t.get('priority','보통')}"
            )
        context_parts.append("[현재 업무 목록]\n" + "\n".join(task_lines))

    return "\n\n".join(context_parts)


def ask_sidebar_chatbot(question: str, current_page: str = "") -> str:
    """사이드바 챗봇 응답 생성. 회의록/분석결과/업무목록을 함께 참고합니다."""
    if not question or not question.strip():
        return "질문을 입력해주세요."
    client = get_openai_client()
    context = build_assistant_context(current_page)
    history = st.session_state.get("able_chat_messages", [])[-8:]
    messages = [
        {
            "role": "system",
            "content": (
                "너는 앱 안에 상주하는 AI 비서 '에이블'이다. "
                "사용자의 회의 분석, 숏폼 전략, 업무 흐름 관리를 도와라. "
                "답변은 한국어로 짧고 실행 가능하게 작성한다. "
                "사용자가 다음에 무엇을 눌러야 할지 물으면 1번, 2번, 3번 순서로 안내한다. "
                "입력 또는 앱 상태에서 확인되지 않는 내용은 추측하지 않는다."
            ),
        },
        {"role": "user", "content": f"[앱 상태 참고]\n{context}"},
    ]
    for m in history:
        if m.get("role") in {"user", "assistant"} and m.get("content"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": question})
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.25,
    )
    return resp.choices[0].message.content


def render_step_guide(current_page: str = ""):
    """사용자가 헷갈리지 않도록 현재 페이지에서 다음 클릭 순서를 보여줍니다."""
    if current_page == "1_dashboard.py":
        steps = [
            "회의록을 붙여넣거나 🎙️ STT로 입력",
            "⚡ 전체 분석 실행 클릭",
            "요약·과제·인사이트 탭 확인",
            "필요하면 업무 대시보드에서 흐름 확인",
        ]
    elif current_page == "2_shortform.py":
        steps = [
            "참고 회의록 확인 또는 저장",
            "🎬 숏폼 전략 생성",
            "🎥 스크립트 생성",
            "필요하면 🔊 음성으로 검토",
        ]
    elif current_page == "3_tasks.py":
        steps = [
            "회의록에서 업무 추출",
            "📊 편집 테이블에서 담당자·상태 정리",
            "🔄 업무 흐름 탭에서 병목 확인",
            "다음 액션 추천 확인",
        ]
    elif current_page == "4_chatbot.py":
        steps = [
            "파일 업로드 또는 질문 입력",
            "필요하면 🎙️ 음성으로 질문",
            "실행 버튼으로 에이블 답변 확인",
            "필요하면 답변을 🔊 음성으로 듣기",
        ]
    else:
        steps = [
            "담당자를 선택해 로그인",
            "회의록 입력 또는 STT 사용",
            "분석 실행 후 결과 확인",
        ]
    lis = "".join([f"<li><b>{i+1}</b><span>{step}</span></li>" for i, step in enumerate(steps)])
    st.markdown(
        f"""<div class="guide-card">
            <div class="guide-title">다음 순서</div>
            <ol class="guide-list">{lis}</ol>
        </div>""",
        unsafe_allow_html=True,
    )


def render_sidebar_chatbot(current_page: str = ""):
    """왼쪽 사이드바에 STT 기반 챗봇을 표시합니다."""
    st.markdown('<div class="sb-section">에이블 챗봇</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="chat-help">음성으로 질문하거나 직접 입력하세요. 현재 회의록과 분석 결과를 참고해 답해요.</div>',
        unsafe_allow_html=True,
    )

    if "able_chat_messages" not in st.session_state:
        st.session_state["able_chat_messages"] = []

    with st.expander("🎙️ 음성 질문", expanded=False):
        audio_question = None
        if hasattr(st, "audio_input"):
            audio_question = st.audio_input("질문 녹음", key=f"chat_audio_{current_page}")
        else:
            audio_question = st.file_uploader(
                "음성 질문 업로드", type=["wav", "mp3", "m4a", "webm"], key=f"chat_audio_upload_{current_page}"
            )
        if st.button("음성을 질문으로 변환", key=f"chat_stt_btn_{current_page}", use_container_width=True):
            if not audio_question:
                st.warning("먼저 음성을 녹음하거나 업로드해주세요.")
            else:
                with st.spinner("질문을 듣는 중…"):
                    transcript = transcribe_audio_file(audio_question)
                if transcript.strip():
                    st.session_state[f"able_chat_input_{current_page}"] = transcript.strip()
                    st.success("질문 입력창에 반영했어요.")
                    st.rerun()
                else:
                    st.warning("음성을 텍스트로 변환하지 못했어요.")

    question = st.text_area(
        "에이블에게 질문",
        key=f"able_chat_input_{current_page}",
        height=74,
        placeholder="예: 다음에 뭘 누르면 돼? / 김대리 업무만 알려줘",
        label_visibility="collapsed",
    )
    c1, c2 = st.columns([2, 1])
    with c1:
        ask_clicked = st.button("질문하기", key=f"chat_ask_{current_page}", use_container_width=True)
    with c2:
        clear_clicked = st.button("초기화", key=f"chat_clear_{current_page}", use_container_width=True)

    if clear_clicked:
        st.session_state["able_chat_messages"] = []
        st.session_state.pop("able_chat_last_audio", None)
        st.rerun()

    if ask_clicked:
        if not question.strip():
            st.warning("질문을 입력해주세요.")
        else:
            with st.spinner("에이블이 답변 중…"):
                answer = ask_sidebar_chatbot(question, current_page)
            st.session_state["able_chat_messages"].append({"role": "user", "content": question.strip()})
            st.session_state["able_chat_messages"].append({"role": "assistant", "content": answer})
            st.session_state.pop("able_chat_last_audio", None)
            st.rerun()

    messages = st.session_state.get("able_chat_messages", [])[-6:]
    if messages:
        st.markdown('<div class="chat-list">', unsafe_allow_html=True)
        for m in messages:
            role_cls = "user" if m.get("role") == "user" else "assistant"
            name = "나" if role_cls == "user" else "에이블"
            content = str(m.get("content", "")).replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            st.markdown(
                f'<div class="chat-msg {role_cls}"><div class="chat-name">{name}</div><div>{content}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)
        last_answer = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "assistant"), "")
        if last_answer:
            if st.button("🔊 마지막 답변 듣기", key=f"chat_tts_{current_page}", use_container_width=True):
                with st.spinner("음성 생성 중…"):
                    st.session_state["able_chat_last_audio"] = synthesize_speech(last_answer, "nova")
            if st.session_state.get("able_chat_last_audio"):
                st.audio(st.session_state["able_chat_last_audio"], format="audio/mp3")
    else:
        st.markdown('<div class="chat-empty">예: “전체 분석 다음에 뭘 누르면 돼?”</div>', unsafe_allow_html=True)

# ── Analysis functions ──
def summarize_meeting(t, length="보통"):
    return ask_ai("회의 핵심 요약", t,
        f"1.회의 목적 2.핵심 논의 3.리브랜딩 논의 4.확정 사항 5.미해결 6.다음 회의 확인 항목 — 길이: {LENGTH_PROMPTS[length]}")

def extract_tasks_ai(t):
    return ask_ai("담당자별 과제 추출", t,
        "| 담당자 | 업무 | 관련 파트 | 마감일 | 우선순위 | 근거 | 형식의 Markdown 표로 정리")

def branding_insight(t):
    return ask_ai("리브랜딩 인사이트", t,
        "1.기존 이미지 문제 2.새 이미지 방향 3.유지할 자산 4.버릴 이미지 5.글로벌 사례 방향 6.팝업 아이디어 7.톤앤매너")

def action_and_risk(t):
    return ask_ai("실행 계획 및 리스크", t,
        "실행 계획 표 (번호|실행항목|담당자|마감일|우선순위|산출물) + 리스크 표 (번호|유형|내용|영향|대응)")

def decisions(t):
    return ask_ai("결정사항 추출", t,
        "| 번호 | 결정사항 | 관련 영역 | 결정 배경 | 후속 조치 | 형식의 표만 작성")

def ask_able(question, reference_text):
    return ask_ai("에이블 Q&A", f"[참고]\n{reference_text}\n\n[질문]\n{question}",
        "1.핵심 답변 2.근거 3.리브랜딩 시사점 4.숏폼 시사점 5.즉시 실행 액션")

def generate_notify_messages(t):
    return ask_ai("담당자별 알림", t,
        "담당자별 슬랙/카카오톡 스타일 알림 메시지. 형식:\n## [담당자명]\n(2~4줄 알림. 이모지 포함.)\n---\n반복",
        temperature=0.4)

def make_email_draft(t, recipient_name, sender_name):
    return ask_ai("이메일 초안",
        f"[회의록]\n{t}\n\n[수신자] {recipient_name} / [발신자] {sender_name}",
        "업무 이메일 톤으로 회의 핵심·담당자 업무·리브랜딩·실행 계획 포함 브리핑. 제목 포함.")

def extract_keywords(t):
    result = ask_ai("핵심 키워드 추출", t,
        '회의에서 중요한 키워드 5~8개 추출. 반드시 JSON만: {"keywords": ["k1","k2",...]} 다른 텍스트 금지.')
    try:
        clean = result.strip().replace("```json", "").replace("```", "")
        return json.loads(clean).get("keywords", [])
    except Exception:
        return re.findall(r'["\']([\w\s가-힣]+)["\']', result)[:8]

def compare_meetings(prev_text, curr_text):
    return ask_ai("회의 간 변화 분석",
        f"[이전]\n{prev_text}\n\n[현재]\n{curr_text}",
        "1.[추가] 추가된 전략/과제 2.[제거] 없어진 항목 3.[변화] 방향 변화 4.[진척] 진척 항목 5.[주의] 주의 필요 변화")

# ── Shortform functions ──
def shortform_strategy(t):
    return ask_ai("숏폼 확산 전략", t,
        "1.핵심 메시지 2.톤앤매너 3.챌린지/밈 4.플랫폼별 방향 5.인플루언서 협업 6.구매 전환 장치 7.저예산 실험안")

def generate_shortform_script(t, concept=""):
    extra = f"\n[컨셉 힌트]: {concept}" if concept.strip() else ""
    return ask_ai("숏폼 스크립트", t + extra,
        "60초 숏폼 스크립트:\n1.Hook(0~3초) 2.전개(3~45초, 대사+장면묘사) 3.CTA(45~60초) 4.BGM 제안 5.플랫폼 추천\n대사는 큰따옴표",
        temperature=0.6)

def generate_ab_test(t):
    return ask_ai("A/B 테스트", t,
        "숏폼 A/B 테스트 3세트. 형식:\n### 테스트[N]: [주제]\n- A안:\n- B안:\n- 측정 지표:\n- 예상 승자:\n---",
        temperature=0.5)

def fetch_related_news(t, keyword=""):
    q = keyword.strip() if keyword.strip() else t[:200]
    result = ask_ai("관련 뉴스", q,
        '마케팅/Z세대/숏폼 트렌드 관련 뉴스 5개. JSON만: {"articles":[{"title":"","source":"","date":"","summary":""},...]}',
        temperature=0.5)
    try:
        clean = result.strip().replace("```json", "").replace("```", "")
        return json.loads(clean).get("articles", [])
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════
# TASK (dashboard) helpers
# ══════════════════════════════════════════════════════════════
def extract_tasks_structured(minutes_text: str) -> list:
    client = get_openai_client()
    prompt = f"""다음 회의록에서 업무를 추출하세요.
담당자 불명 → "미정", 마감일 불명 → "미정", 상태 기본값 → "진행 예정", 우선순위 → "높음"/"보통"/"낮음"

회의록:
{minutes_text}

JSON 형식으로만 답변:
{{"tasks":[{{"title":"","description":"","assignee":"","status":"진행 예정","priority":"보통","due_date":"미정"}}]}}"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "회의록에서 업무를 구조화하는 AI입니다."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        raw = resp.choices[0].message.content.strip().replace("```json","").replace("```","")
        return json.loads(raw).get("tasks", [])
    except Exception:
        return []

def add_tasks_to_state(new_tasks: list) -> int:
    if "tasks" not in st.session_state:
        st.session_state["tasks"] = []
    for task in new_tasks:
        task["task_id"] = len(st.session_state["tasks"]) + 1
        st.session_state["tasks"].append(task)
    return len(new_tasks)

# ══════════════════════════════════════════════════════════════
# SHARED SIDEBAR
# ══════════════════════════════════════════════════════════════
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Pretendard:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; height: 0 !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton { display: none !important; }
[data-testid="stHeader"] { height: 0 !important; background: transparent !important; }
[data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; opacity: 1 !important; }
.stApp { background: #F7F4FF !important; }
[data-testid="stAppViewContainer"] { background: #F7F4FF !important; }

/* ── NAV SIDEBAR ── */
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    background: #FFFFFF !important;
    border-right: 1px solid #E5DDF7 !important;
    min-width: 220px !important;
    width: 250px !important;
}
section[data-testid="stSidebar"] * { color: #2E2940 !important; }

.sb-profile {
    background: #FFFFFF; border: 1px solid #DDD3F2;
    border-radius: 14px; padding: 1rem 1.1rem;
    text-align: center; margin-bottom: 1.2rem;
}
.sb-emoji { font-size: 2.2rem; margin-bottom: 0.3rem; }
.sb-name { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; color: #211A32 !important; }
.sb-role { font-size: 0.72rem; color: #7C738F !important; margin-top: 2px; letter-spacing: 0.06em; }

.sb-section { font-size: 0.63rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #8F86A3 !important; margin: 1.2rem 0 0.5rem; }

.nav-item {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.52rem 0.8rem; border-radius: 10px;
    font-size: 0.84rem; font-weight: 500;
    color: #5F5671 !important; margin-bottom: 2px;
    transition: background 0.15s;
    text-decoration: none;
}
.nav-item:hover { background: #F1ECFF !important; color: #2E2940 !important; }
.nav-item.active { background: #EEE7FF !important; color: #7C5CFF !important; }
.nav-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

/* ── PAGE COMMON ── */
.block-container { padding: 0.65rem 2.5rem 2.5rem !important; max-width: 1100px !important; }

.page-header {
    margin-bottom: 1.2rem;
    padding-bottom: 0.85rem;
    border-bottom: 1px solid #E6DDF7;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.65rem; font-weight: 800;
    color: #211A32;
    letter-spacing: -0.02em;
    margin: 0 0 0.25rem;
}
.page-subtitle { font-size: 0.83rem; color: #6F6682; margin: 0; }

/* ── CARDS ── */
.card {
    background: #FFFFFF; border: 1px solid #E5DDF7;
    border-radius: 14px; padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #6F6682; margin-bottom: 0.7rem;
}

/* ── INPUT OVERRIDES ── */
textarea, input[type="text"], .stTextInput input, .stTextArea textarea {
    background: #FFFFFF !important; color: #2E2940 !important;
    border: 1px solid #E5DDF7 !important; border-radius: 10px !important;
}
textarea:focus, input:focus {
    border-color: #9A80FF !important;
    box-shadow: 0 0 0 3px rgba(99,85,180,0.12) !important;
}
.stSelectbox > div { background: #FFFFFF !important; border: 1px solid #E5DDF7 !important; border-radius: 10px !important; }
.stSelectbox [data-baseweb="select"] > div { min-height: 46px !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: #F1ECFF !important; color: #7C5CFF !important;
    border: 1px solid #D5C8EE !important; border-radius: 10px !important;
    font-family: 'Pretendard', sans-serif !important;
    font-size: 0.85rem !important; font-weight: 600 !important;
    padding: 0.5rem 1.1rem !important;
    min-height: 46px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #E9E0FF !important; border-color: #B49DFF !important;
    transform: translateY(-1px) !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: #FFFFFF !important;
    border: 1px solid #E5DDF7 !important;
    color: #4A4358 !important;
    border-radius: 10px !important;
    min-height: 34px !important;
    padding: 0.35rem 0.55rem !important;
    font-size: 0.78rem !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #F1ECFF !important;
    color: #7C5CFF !important;
    border-color: #D5C8EE !important;
}

/* Primary button variant */
.btn-primary > button {
    background: linear-gradient(120deg, #8B6CFF 0%, #6B3D6E 100%) !important;
    color: #FFFFFF !important; border: none !important;
}
.btn-primary > button:hover {
    background: linear-gradient(120deg, #7C5CFF 0%, #7D4880 100%) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important; border-radius: 12px !important;
    gap: 2px !important; padding: 4px !important;
    border: 1px solid #E5DDF7 !important;
    margin-top: 0.2rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #6F6682 !important;
    border-radius: 8px !important; font-size: 0.82rem !important;
    font-weight: 600 !important; padding: 0.45rem 0.9rem !important;
}
.stTabs [aria-selected="true"] {
    background: #EEE7FF !important; color: #7C5CFF !important;
}


/* ── LIGHTER GLOBAL READABILITY ── */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stCaption, label, .stRadio label, .stSelectbox label {
    color: #2E2940 !important;
}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {
    background: #FFFFFF !important;
    border-radius: 12px !important;
}
[data-testid="stMetric"] {
    background: #FFFFFF !important;
}
.stAlert {
    background: #FFFFFF !important;
    color: #2E2940 !important;
    border: 1px solid #E5DDF7 !important;
}

/* ── MISC ── */
hr { border-color: #E6DDF7 !important; }
.stSuccess, .stInfo, .stWarning { border-radius: 10px !important; }
.stSpinner > div { border-color: #7C5CFF !important; }

/* keyword tags */
.kw-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin: 0.6rem 0; }
.kw-tag {
    background: #F1ECFF; border: 1px solid #D5C8EE;
    border-radius: 20px; padding: 3px 12px;
    font-size: 0.76rem; font-weight: 600; color: #7C5CFF;
}

/* notify / news cards */
.n-card { background: #FFFFFF; border: 1px solid #E5DDF7; border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.7rem; }
.n-card-title { font-size: 0.85rem; font-weight: 700; color: #E94C98; margin-bottom: 0.4rem; }
.n-card-body { font-size: 0.82rem; color: #5F5671; line-height: 1.65; }
.news-source { font-size: 0.7rem; color: #6F6682; font-weight: 600; margin-bottom: 0.3rem; }
.news-title { font-size: 0.92rem; font-weight: 700; color: #2E2940; margin-bottom: 0.4rem; }
.news-body { font-size: 0.8rem; color: #766D8A; line-height: 1.6; }

/* progress bar */
.prog-wrap { background: #F1ECFF; border-radius: 6px; height: 8px; overflow: hidden; margin: 6px 0 14px; }
.prog-fill { background: linear-gradient(90deg, #7C5CFF, #E94C98); height: 100%; border-radius: 6px; transition: width 0.4s; }


/* ── TOP ACTION ALIGNMENT / AUDIO AREAS ── */
.audio-box {
    background:#FFFFFF; border:1px dashed #D5C8EE; border-radius:12px;
    padding:0.9rem 1rem; margin:0.6rem 0 0.8rem;
}
.audio-help { font-size:0.76rem; color:#766D8A; margin-bottom:0.45rem; }
[data-testid="stHorizontalBlock"] { align-items: center; }
.stTabs [data-baseweb="tab-list"] { margin-top: 0.4rem !important; }

/* ── SIDEBAR GUIDE / CHATBOT ── */
.guide-card {
    background:#FFFFFF; border:1px solid #E5DDF7; border-radius:14px;
    padding:0.85rem 0.9rem; margin:0.5rem 0 1rem;
    box-shadow:0 4px 14px rgba(124,92,255,0.06);
}
.guide-title { font-size:0.78rem; font-weight:800; color:#7C5CFF; margin-bottom:0.45rem; }
.guide-list { margin:0; padding-left:0; list-style:none; }
.guide-list li { display:flex; gap:0.5rem; align-items:flex-start; margin:0.34rem 0; color:#4A4358; font-size:0.74rem; line-height:1.35; }
.guide-list b { display:inline-flex; align-items:center; justify-content:center; min-width:18px; height:18px; border-radius:50%; background:#EEE7FF; color:#7C5CFF; font-size:0.68rem; }
.chat-help { font-size:0.72rem; line-height:1.45; color:#766D8A; margin:0.25rem 0 0.55rem; }
.chat-empty { font-size:0.72rem; color:#A79ABF; background:#FFFFFF; border:1px dashed #E5DDF7; border-radius:12px; padding:0.7rem; margin-top:0.45rem; }
.chat-list { margin-top:0.55rem; }
.chat-msg { border-radius:12px; padding:0.65rem 0.75rem; margin-bottom:0.45rem; font-size:0.74rem; line-height:1.5; }
.chat-msg.user { background:#EEE7FF; color:#352A52; border:1px solid #D5C8EE; }
.chat-msg.assistant { background:#FFFFFF; color:#2E2940; border:1px solid #E5DDF7; }
.chat-name { font-size:0.66rem; font-weight:800; color:#7C5CFF; margin-bottom:0.18rem; }
section[data-testid="stSidebar"] textarea { min-height:70px !important; font-size:0.78rem !important; }
section[data-testid="stSidebar"] .stExpander { border-color:#E5DDF7 !important; }


/* ── READABILITY FIX: prevent white text on light background ── */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
label,
label p,
label span {
    color: #211A32 !important;
}

/* Placeholder text */
input::placeholder,
textarea::placeholder,
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #9A90AA !important;
    opacity: 1 !important;
}

/* Expander labels: STT, TTS, 참고 회의록 등 */
[data-testid="stExpander"] details summary,
[data-testid="stExpander"] details summary *,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *,
.streamlit-expanderHeader,
.streamlit-expanderHeader * {
    color: #211A32 !important;
}

/* Radio / Checkbox / Selectbox */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label *,
div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] label *,
div[data-testid="stSelectbox"] label,
div[data-testid="stSelectbox"] label * {
    color: #211A32 !important;
}

/* Text inputs and search keyword fields */
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] label *,
div[data-testid="stTextArea"] label,
div[data-testid="stTextArea"] label *,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    color: #211A32 !important;
}

/* Alert boxes */
[data-testid="stAlert"],
[data-testid="stAlert"] *,
.stAlert,
.stAlert * {
    color: #211A32 !important;
}

/* Download and expander buttons */
.stDownloadButton > button,
.stDownloadButton > button *,
.stButton > button,
.stButton > button * {
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif !important;
}

/* Meeting input area */
.meeting-input-head {
    background: #FFFFFF;
    border: 1px solid #E5DDF7;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.85rem;
}
.meeting-input-title {
    font-size: 0.95rem;
    font-weight: 800;
    color: #211A32 !important;
    margin-bottom: 0.25rem;
}
.meeting-input-desc {
    font-size: 0.78rem;
    color: #6F6682 !important;
    line-height: 1.5;
}
.meeting-char-count {
    color: #6F6682 !important;
    font-size: 0.74rem;
    text-align: right;
    padding-top: 0.8rem;
}

/* File uploader label readability */
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] label * {
    color: #211A32 !important;
}

</style>
"""

def render_sidebar(current_page: str = ""):
    user = st.session_state.get("logged_in_user")
    if not user:
        st.switch_page("app.py")
        return
    meta = ROLES.get(user, {})
    color = meta.get("color", "#7C5CFF")

    with st.sidebar:
        if os.path.exists(ABLE_IMAGE_PATH):
            st.markdown('<div class="sb-mascot">', unsafe_allow_html=True)
            st.image(ABLE_IMAGE_PATH, width=86)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sb-profile" style="border-color:{color}22;">
            <div class="sb-emoji">{meta.get('emoji','✨')}</div>
            <div class="sb-name">{user}</div>
            <div class="sb-role" style="color:{color} !important;">{meta.get('title','')} · {meta.get('desc','')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-section">메인 메뉴</div>', unsafe_allow_html=True)

        pages = [
            ("1_dashboard.py",  "📋", "회의 분석 대시보드"),
            ("2_shortform.py",  "🎬", "숏폼 스튜디오"),
            ("3_tasks.py",      "✅", "업무 대시보드"),
            ("4_chatbot.py",    "🤖", "에이블 챗봇"),
        ]
        for page_file, icon, label in pages:
            is_active = current_page == page_file
            if is_active:
                st.markdown(
                    f'<div class="nav-item active">'
                    f'<span class="nav-dot" style="background:{color};"></span>'
                    f'{icon} {label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon} {label}", key=f"nav_{page_file}", use_container_width=True):
                    st.switch_page(f"pages/{page_file}")

        render_step_guide(current_page)

        st.markdown('<div class="sb-section">히스토리</div>', unsafe_allow_html=True)
        history = st.session_state.get("history", [])
        if history:
            for i, snap in enumerate(reversed(history[-3:])):
                preview = snap["text"][:35].replace("\n", " ") + "…"
                st.markdown(
                    f'<div style="font-size:0.75rem;color:#6F6682;padding:4px 8px;margin-bottom:3px;">'
                    f'<span style="color:#9A80FF;">#{len(history)-i}</span> {preview}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div style="font-size:0.75rem;color:#D5C8EE;padding:4px 8px;">저장된 히스토리 없음</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("👋 로그아웃", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")
