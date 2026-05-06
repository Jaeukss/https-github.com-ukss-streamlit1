# -*- coding: utf-8 -*-
# pages/4_chatbot.py — 에이블 챗봇
import sys, os, json, base64, requests, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from openai import OpenAI
from shared import (
    GLOBAL_CSS, ROLES, PROJECT_CONTEXT, OPENAI_API_KEY, SENDGRID_API_KEY, EMAIL_ADDRESS,
    render_sidebar, transcribe_audio_file, synthesize_speech, build_assistant_context,
)

st.set_page_config(
    page_title="에이블 · 챗봇",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not st.session_state.get("logged_in_user"):
    st.switch_page("app.py")

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
render_sidebar(current_page="4_chatbot.py")

user = st.session_state["logged_in_user"]
meta = ROLES[user]
color = meta["color"]

st.markdown(f"""
<div class="page-header">
    <div class="page-title">에이블 챗봇</div>
    <div class="page-subtitle" style="color:{color};">
        {meta['emoji']} {user} · 음성/STT 질문 · 텍스트 질문 · 이메일 발송 · TTS 답변
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div class="card-title">사용 방법</div>
    <div style="font-size:0.86rem;color:#6F6682;line-height:1.75;">
        1. 회의록이나 참고 텍스트가 있으면 파일을 업로드하세요.<br>
        2. 텍스트로 질문하거나 음성으로 질문을 녹음하세요.<br>
        3. <b>실행</b>을 누르면 에이블이 현재 앱의 회의록/분석 결과/업무 목록까지 참고해서 답합니다.<br>
        4. 답변은 필요할 때 음성으로 다시 들을 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 챗봇 전용 상태
# ══════════════════════════════════════════════════════════════
if "voice_chat_messages" not in st.session_state:
    st.session_state["voice_chat_messages"] = [
        {"role": "assistant", "content": "안녕하세요. 에이블 챗봇입니다. 회의 요약, 업무 확인, 이메일 초안/발송을 도와드릴게요."}
    ]
if "voice_chat_last_audio" not in st.session_state:
    st.session_state["voice_chat_last_audio"] = None
if "voice_chat_transcript" not in st.session_state:
    st.session_state["voice_chat_transcript"] = ""


def send_email(to: str, subject: str, body: str) -> dict:
    """SendGrid로 이메일을 발송합니다. 발신자는 인증된 mememeco8@gmail.com으로 고정합니다."""
    if not SENDGRID_API_KEY:
        return {"status": "failed", "error": "SENDGRID_API_KEY가 설정되어 있지 않습니다."}
    if not to or "@" not in to:
        return {"status": "failed", "error": "수신자 이메일 주소를 확인해주세요."}

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "personalizations": [{"to": [{"email": to}], "subject": subject}],
        "from": {"email": EMAIL_ADDRESS, "name": "에이블"},
        "content": [{"type": "text/plain", "value": body}],
    }
    response = requests.post("https://api.sendgrid.com/v3/mail/send", headers=headers, json=data, timeout=20)
    if response.status_code == 202:
        return {"status": "success", "message": "이메일 발송에 성공했습니다."}
    return {"status": "failed", "error": response.text}


def decode_uploaded_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    raw = uploaded_file.read()
    for enc in ("utf-8", "cp949", "euc-kr"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def build_system_prompt(reference_text: str = "") -> str:
    app_context = build_assistant_context("4_chatbot.py")
    role = f"""
당신은 '{user}'의 개인 비서 '에이블'입니다.
사용자가 요청한 업무를 친절하고 실행 가능하게 처리합니다.
주요 업무는 회의 내용 요약, 담당 업무 확인, 다음 순서 안내, 이메일 초안 작성 및 발송 보조입니다.
답변은 한국어로 작성하고, 확인되지 않은 내용은 추측하지 않습니다.
이메일 발송 요청이 명확하면 send_email 도구를 사용합니다.
"""
    if reference_text.strip():
        role += f"\n[사용자가 업로드한 참고 텍스트]\n{reference_text[:5000]}\n"
    role += f"\n[프로젝트 배경]\n{PROJECT_CONTEXT}\n\n[현재 앱 상태]\n{app_context[:6000]}"
    return role


def ask_chatbot(user_request: str, reference_text: str = "") -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)
    tools = [{
        "type": "function",
        "name": "send_email",
        "description": "이메일을 발송합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "이메일 수신자. 예: test@gmail.com"},
                "subject": {"type": "string", "description": "이메일 제목"},
                "body": {"type": "string", "description": "이메일 본문"},
            },
            "required": ["to", "subject", "body"],
            "additionalProperties": False,
        },
        "strict": True,
    }]

    input_messages = [{"role": "system", "content": build_system_prompt(reference_text)}]
    input_messages += st.session_state["voice_chat_messages"][-8:]
    input_messages.append({"role": "user", "content": user_request})

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=input_messages,
            tools=tools,
            tool_choice="auto",
        )
        tool_calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
        if not tool_calls:
            return response.output_text

        tool_outputs = []
        for item in tool_calls:
            args = json.loads(item.arguments)
            if item.name == "send_email":
                result = send_email(**args)
                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                })

        final_response = client.responses.create(
            model="gpt-4o-mini",
            previous_response_id=response.id,
            input=tool_outputs,
        )
        return final_response.output_text
    except Exception as e:
        return f"오류가 발생했습니다: {e}"


with st.form("able_voice_chat_form"):
    uploaded_file = st.file_uploader("참고 텍스트 파일 업로드", type=["txt", "md"])

    text_value = st.text_area(
        "텍스트로 요청하기",
        value=st.session_state.get("voice_chat_transcript", ""),
        height=120,
        placeholder="예: 회의록을 요약해서 팀장님에게 보낼 이메일 초안을 써줘 / 김대리 업무만 알려줘",
    )

    audio_value = None
    if hasattr(st, "audio_input"):
        audio_value = st.audio_input("음성으로 요청하기")
    else:
        audio_value = st.file_uploader("음성 파일 업로드", type=["wav", "mp3", "m4a", "webm"])

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        submit = st.form_submit_button("실행", use_container_width=True)
    with c2:
        transcribe_only = st.form_submit_button("STT만 변환", use_container_width=True)
    with c3:
        clear_chat = st.form_submit_button("대화 초기화", use_container_width=True)

if clear_chat:
    st.session_state["voice_chat_messages"] = [
        {"role": "assistant", "content": "대화를 초기화했어요. 무엇을 도와드릴까요?"}
    ]
    st.session_state["voice_chat_last_audio"] = None
    st.session_state["voice_chat_transcript"] = ""
    st.rerun()

if transcribe_only:
    if not audio_value:
        st.warning("먼저 음성을 녹음하거나 업로드해주세요.")
    else:
        with st.spinner("음성을 텍스트로 변환하고 있습니다…"):
            transcript = transcribe_audio_file(audio_value)
        st.session_state["voice_chat_transcript"] = transcript
        st.success("STT 변환 완료. 입력창에 반영했어요.")
        st.rerun()

if submit:
    reference_text = decode_uploaded_text(uploaded_file)

    user_request = text_value.strip()
    if not user_request and audio_value is not None:
        with st.spinner("음성을 텍스트로 변환하고 있습니다…"):
            user_request = transcribe_audio_file(audio_value).strip()
        if user_request:
            st.session_state["voice_chat_transcript"] = user_request
            st.info(f"STT 인식 결과: {user_request}")

    if not user_request:
        st.warning("텍스트를 입력하거나 음성을 녹음해주세요.")
        st.stop()

    st.session_state["voice_chat_messages"].append({"role": "user", "content": user_request})
    with st.spinner("에이블이 답변을 준비하고 있습니다…"):
        answer = ask_chatbot(user_request, reference_text)
    st.session_state["voice_chat_messages"].append({"role": "assistant", "content": answer})
    st.session_state["voice_chat_messages"] = st.session_state["voice_chat_messages"][-12:]
    st.session_state["voice_chat_last_audio"] = None
    st.session_state["voice_chat_transcript"] = ""
    st.rerun()

st.markdown("---")

for message in st.session_state["voice_chat_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

last_answer = next((m.get("content", "") for m in reversed(st.session_state["voice_chat_messages"]) if m.get("role") == "assistant"), "")
if last_answer:
    st.markdown("---")
    tts_col, audio_col = st.columns([1, 3])
    with tts_col:
        if st.button("🔊 마지막 답변 듣기", use_container_width=True):
            with st.spinner("음성 답변 생성 중…"):
                st.session_state["voice_chat_last_audio"] = synthesize_speech(last_answer, "nova")
    with audio_col:
        if st.session_state.get("voice_chat_last_audio"):
            st.audio(st.session_state["voice_chat_last_audio"], format="audio/mp3")
