import os
import requests
import streamlit as st
from openai import OpenAI


st.set_page_config(
    page_title="에이블 | Z세대 리브랜딩 전략 AI 비서",
    page_icon="🧠",
    layout="wide"
)

st.caption("APP VERSION: able-colab-streamlit-v2")


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
    st.error("OPENAI_API_KEY가 없습니다. Colab에서 환경변수를 먼저 설정하세요.")
    st.stop()


client = OpenAI(api_key=OPENAI_API_KEY)


PROJECT_CONTEXT = """
[프로젝트 배경 및 문제 정의]

1. 핵심 과제:
전통의 현대화 - Z세대 타겟 리브랜딩 및 숏폼 확산 전략

20년 된 장수 브랜드의 '아빠 브랜드' 이미지를 탈피하기 위해,
브랜드 정체성을 재정립함과 동시에 저예산 고효율 매체인 숏폼을 활용하여
Z세대에게 브랜드 인지도를 확산시키는 것을 목표로 한다.

2. 현재 상황 및 당면 문제

브랜드 위기:
- 장수 브랜드로서의 신뢰도는 높으나, 1020 세대와의 접점이 없어 신규 유입이 단절됨.

자원 한계:
- 대규모 TV CF 등 전통적 광고 예산은 제한적임.
- 아이디어 고갈로 인해 디지털 트렌드 대응력이 낮아진 상태.

전략적 공백:
- Z세대가 좋아하는 톤앤매너와 구매로 이어지는 숏폼 마케팅 공식에 대한 데이터가 부족함.

3. 주요 수행 업무

Part 1. 브랜드 이미지 쇄신 로직
- 글로벌 성공 사례 분석
- Z세대 커뮤니케이션 방식, 톤앤매너, 팝업스토어 트렌드 조사

Part 2. 디지털 확산 및 전환 전략
- 숏폼 성공 공식 도출
- 인플루언서 협업 성공 사례 리서치

4. AI 비서 에이블의 역할
- 회의 분석
- 담당자별 업무 구분
- 리브랜딩 및 숏폼 전략 질의응답
- 이메일 브리핑 생성 및 발송
"""


DEFAULT_MEETING1_TEXT = """
오늘 회의에서는 20년 된 장수 브랜드의 Z세대 리브랜딩 방향을 논의했다.
현재 브랜드는 신뢰도는 높지만 1020 세대에게는 아빠 브랜드 이미지가 강하다는 점이 문제로 제기되었다.

김 대리는 올드스파이스와 구찌의 리브랜딩 사례를 조사하기로 했다.
박 대리는 최근 3개월간 틱톡과 릴스에서 바이럴된 챌린지 사례를 정리하기로 했다.
이 과장은 인플루언서 협업을 통한 구매 전환 사례를 조사하기로 했다.

팀에서는 대규모 TV 광고보다 숏폼 중심의 저예산 확산 전략이 필요하다고 판단했다.
다만 브랜드 정체성을 훼손하지 않으면서 Z세대에게 어색하지 않은 톤앤매너를 찾는 것이 중요하다는 의견이 있었다.

다음 회의 전까지 각자 조사한 내용을 공유하고, 이를 바탕으로 숏폼 챌린지 아이디어를 3개 이상 제안하기로 했다.
"""


def ask_ai(task_title: str, user_input: str, output_instruction: str) -> str:
    if not user_input or not user_input.strip():
        return "입력 내용이 없습니다."

    prompt = f"""
너는 AI 비서 '에이블'이다.

아래 프로젝트 배경을 반영하라.

{PROJECT_CONTEXT}

[분석 목적]
{task_title}

[사용자 입력]
{user_input}

[출력 지시]
{output_instruction}

[공통 규칙]
- 한국어로 작성
- 입력에 없는 사실은 추측하지 말 것
- 불확실한 정보는 "입력 내용에서 확인 불가"라고 표시
- 표가 적합하면 Markdown 표로 작성
- Z세대 리브랜딩과 숏폼 확산 전략 관점에서 해석
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "너는 Z세대 리브랜딩과 숏폼 확산 전략을 지원하는 AI 비서 에이블이다."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def summarize_meeting(meeting1_text: str) -> str:
    return ask_ai(
        "회의 핵심 요약",
        meeting1_text,
        """
다음 항목으로 정리하라.

1. 회의 목적
2. 핵심 논의 내용
3. 리브랜딩 관련 논의
4. 숏폼 확산 전략 관련 논의
5. 확정된 내용
6. 미해결 사항
7. 다음 회의에서 확인할 사항
"""
    )


def extract_tasks(meeting1_text: str) -> str:
    return ask_ai(
        "담당자별 리서치 및 실행 과제 추출",
        meeting1_text,
        """
회의록에서 담당자별 업무를 추출하라.

| 담당자 | 업무 | 관련 파트 | 마감일 | 우선순위 | 근거 |
|---|---|---|---|---|---|

관련 파트:
- 브랜드 이미지 쇄신
- Z세대 타겟팅
- 숏폼 성공 공식
- 퍼포먼스 마케팅
- 실행 관리
- 기타
"""
    )


def branding_insight(meeting1_text: str) -> str:
    return ask_ai(
        "리브랜딩 인사이트 도출",
        meeting1_text,
        """
다음 항목으로 정리하라.

1. 기존 브랜드 이미지 문제
2. Z세대에게 새롭게 보여줘야 할 브랜드 이미지
3. 유지해야 할 기존 브랜드 자산
4. 버려야 할 낡은 이미지
5. 참고 가능한 글로벌 사례 방향
6. 팝업스토어 또는 공간 경험 아이디어
7. 커뮤니케이션 톤앤매너 제안
"""
    )


def shortform_strategy(meeting1_text: str) -> str:
    return ask_ai(
        "숏폼 확산 전략 도출",
        meeting1_text,
        """
다음 항목으로 정리하라.

1. 숏폼 콘텐츠 핵심 메시지
2. Z세대가 반응할 만한 톤앤매너
3. 챌린지 또는 밈 아이디어
4. 틱톡, 릴스, 쇼츠별 활용 방향
5. 인플루언서 협업 방향
6. 조회수 이후 구매 전환 장치
7. 저예산 콘텐츠 실험안
"""
    )


def action_and_risk(meeting1_text: str) -> str:
    return ask_ai(
        "실행 계획 및 리스크 분석",
        meeting1_text,
        """
먼저 실행 계획 표를 작성하라.

| 번호 | 실행 항목 | 담당자 | 마감일 | 우선순위 | 산출물 |
|---|---|---|---|---|---|

다음으로 리스크 표를 작성하라.

| 번호 | 리스크 유형 | 리스크 내용 | 영향 | 대응 방안 |
|---|---|---|---|---|

리스크 유형:
- 브랜드 정체성 훼손
- Z세대 부적합
- 숏폼 확산 실패
- 구매 전환 약함
- 리서치 부족
- 실행 리소스 부족
- 기타
"""
    )


def decisions(meeting1_text: str) -> str:
    return ask_ai(
        "전략 결정사항 추출",
        meeting1_text,
        """
회의에서 확정된 결정사항만 추출하라.

| 번호 | 결정사항 | 관련 영역 | 결정 배경 | 후속 조치 | 근거 |
|---|---|---|---|---|---|
"""
    )


def ask_able(question: str, reference_text: str) -> str:
    return ask_ai(
        "에이블 전략 질의응답",
        f"""
[참고 자료]
{reference_text}

[질문]
{question}
""",
        """
답변 구조:
1. 핵심 답변
2. 근거
3. 리브랜딩 관점 시사점
4. 숏폼 전략 관점 시사점
5. 바로 실행할 수 있는 액션
"""
    )


def send_email(to: str, subject: str, body: str) -> dict:
    if not SENDGRID_API_KEY:
        return {
            "status": "failed",
            "error": "SENDGRID_API_KEY가 없습니다."
        }

    if not to or "@" not in to:
        return {
            "status": "failed",
            "error": "수신자 이메일 주소가 올바르지 않습니다."
        }

    url = "https://api.sendgrid.com/v3/mail/send"

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "personalizations": [
            {
                "to": [{"email": to}],
                "subject": subject
            }
        ],
        "from": {"email": EMAIL_ADDRESS},
        "content": [
            {
                "type": "text/plain",
                "value": body
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)

        if response.status_code == 202:
            return {"status": "success"}

        return {
            "status": "failed",
            "status_code": response.status_code,
            "error": response.text
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


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
        st.session_state.pop(key, None)


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
        if key in st.session_state:
            report += title + "\n\n"
            report += st.session_state[key] + "\n\n"

    if include_email and "email_draft_result" in st.session_state:
        report += "# 8. 이메일 초안\n\n"
        report += st.session_state["email_draft_result"] + "\n\n"

    return report


def run_all_analysis(meeting1_text):
    st.session_state["summary_result"] = summarize_meeting(meeting1_text)
    st.session_state["tasks_result"] = extract_tasks(meeting1_text)
    st.session_state["branding_result"] = branding_insight(meeting1_text)
    st.session_state["shortform_result"] = shortform_strategy(meeting1_text)
    st.session_state["action_risk_result"] = action_and_risk(meeting1_text)
    st.session_state["decisions_result"] = decisions(meeting1_text)


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
        """
아래 형식으로 이메일 초안을 작성하라.

제목:
[에이블 브리핑] Z세대 리브랜딩 및 숏폼 확산 전략 회의 정리

본문:
- 업무용 이메일 톤
- 회의 핵심 요약
- 담당자별 할 일
- 리브랜딩 인사이트
- 숏폼 전략
- 실행 계획
- 확인 필요한 사항
- 마무리 문장
"""
    )


st.title("에이블 | Z세대 리브랜딩 전략 AI 비서")

st.write(
    "회의록을 입력하면 리브랜딩 인사이트, 숏폼 확산 전략, 담당자별 과제, 실행 리스크, 전략 질의응답, 이메일 브리핑 초안을 생성하고 SendGrid로 발송합니다."
)

with st.expander("프로젝트 배경 보기"):
    st.markdown(PROJECT_CONTEXT)

with st.expander("시스템 설정 확인"):
    st.write("OpenAI API Key 로드:", bool(OPENAI_API_KEY))
    st.write("SendGrid API Key 로드:", bool(SENDGRID_API_KEY))
    st.write("발신자 이메일:", EMAIL_ADDRESS)

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

col_input_1, col_input_2 = st.columns([1, 1])

with col_input_1:
    if st.button("예시 회의록 불러오기", use_container_width=True):
        st.session_state["meeting1_text"] = DEFAULT_MEETING1_TEXT
        clear_results()
        st.rerun()

with col_input_2:
    if st.button("입력창 비우기", use_container_width=True):
        st.session_state["meeting1_text"] = ""
        clear_results()
        st.rerun()

meeting1_text = st.text_area(
    "meeting1_text",
    key="meeting1_text",
    height=300,
    placeholder="회의록 내용을 입력하세요."
)

st.write("현재 회의록 글자 수:", len(meeting1_text))

col_action_1, col_action_2 = st.columns([1, 1])

with col_action_1:
    if st.button("전체 분석 실행", use_container_width=True):
        with st.spinner("에이블이 전체 분석 중입니다..."):
            run_all_analysis(meeting1_text)

with col_action_2:
    if st.button("분석 결과 초기화", use_container_width=True):
        clear_results()
        st.rerun()

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "1. 회의 요약",
    "2. 담당자별 과제",
    "3. 리브랜딩 인사이트",
    "4. 숏폼 전략",
    "5. 실행 계획·리스크",
    "6. 결정사항",
    "7. 에이블 Q&A",
    "8. 이메일 발송"
])

with tab1:
    st.subheader("1. 회의 핵심 요약")

    if st.button("회의 요약 생성", key="summary_btn"):
        with st.spinner("회의 요약 생성 중..."):
            st.session_state["summary_result"] = summarize_meeting(meeting1_text)

    if "summary_result" in st.session_state:
        st.markdown(st.session_state["summary_result"])
    else:
        st.info("아직 회의 요약 결과가 없습니다.")

with tab2:
    st.subheader("2. 담당자별 리서치 과제")

    if st.button("담당자별 과제 추출", key="tasks_btn"):
        with st.spinner("담당자별 과제 추출 중..."):
            st.session_state["tasks_result"] = extract_tasks(meeting1_text)

    if "tasks_result" in st.session_state:
        st.markdown(st.session_state["tasks_result"])
    else:
        st.info("아직 담당자별 과제 결과가 없습니다.")

with tab3:
    st.subheader("3. 리브랜딩 인사이트")

    if st.button("리브랜딩 인사이트 생성", key="branding_btn"):
        with st.spinner("리브랜딩 인사이트 생성 중..."):
            st.session_state["branding_result"] = branding_insight(meeting1_text)

    if "branding_result" in st.session_state:
        st.markdown(st.session_state["branding_result"])
    else:
        st.info("아직 리브랜딩 인사이트 결과가 없습니다.")

with tab4:
    st.subheader("4. 숏폼 확산 전략")

    if st.button("숏폼 전략 생성", key="shortform_btn"):
        with st.spinner("숏폼 전략 생성 중..."):
            st.session_state["shortform_result"] = shortform_strategy(meeting1_text)

    if "shortform_result" in st.session_state:
        st.markdown(st.session_state["shortform_result"])
    else:
        st.info("아직 숏폼 전략 결과가 없습니다.")

with tab5:
    st.subheader("5. 실행 계획 및 리스크")

    if st.button("실행 계획·리스크 생성", key="action_risk_btn"):
        with st.spinner("실행 계획 및 리스크 생성 중..."):
            st.session_state["action_risk_result"] = action_and_risk(meeting1_text)

    if "action_risk_result" in st.session_state:
        st.markdown(st.session_state["action_risk_result"])
    else:
        st.info("아직 실행 계획 및 리스크 결과가 없습니다.")

with tab6:
    st.subheader("6. 전략 결정사항")

    if st.button("결정사항 추출", key="decisions_btn"):
        with st.spinner("결정사항 추출 중..."):
            st.session_state["decisions_result"] = decisions(meeting1_text)

    if "decisions_result" in st.session_state:
        st.markdown(st.session_state["decisions_result"])
    else:
        st.info("아직 결정사항 결과가 없습니다.")

with tab7:
    st.subheader("7. 에이블 Q&A")

    question = st.text_input(
        "에이블에게 질문하기",
        value="리브랜딩을 위해 참고할 만한 글로벌 사례와 숏폼 챌린지 성공 공식은 뭐야?"
    )

    if st.button("질문하기", key="qa_btn"):
        with st.spinner("에이블이 답변 생성 중..."):
            st.session_state["qa_result"] = ask_able(
                question=question,
                reference_text=meeting1_text + "\n\n" + build_report_text(include_email=False)
            )

    if "qa_result" in st.session_state:
        st.markdown(st.session_state["qa_result"])
    else:
        st.info("아직 질의응답 결과가 없습니다.")

with tab8:
    st.subheader("8. 이메일 초안 생성 및 SendGrid 발송")

    recipient_name = st.text_input("수신자명", value="팀장님")
    recipient_email = st.text_input("수신자 이메일", value="")
    sender_name = st.text_input("발신자명", value="에이블")

    email_subject = st.text_input(
        "이메일 제목",
        value="[에이블 브리핑] Z세대 리브랜딩 및 숏폼 확산 전략 회의 정리"
    )

    if st.button("이메일 초안 생성", key="email_btn"):
        with st.spinner("이메일 초안 생성 중..."):
            st.session_state["email_draft_result"] = make_email_draft(
                meeting1_text=meeting1_text,
                recipient_name=recipient_name,
                sender_name=sender_name
            )

    if "email_draft_result" in st.session_state:
        email_body = st.text_area(
            "이메일 본문",
            value=st.session_state["email_draft_result"],
            height=420
        )

        col_email_1, col_email_2 = st.columns([1, 1])

        with col_email_1:
            st.download_button(
                label="이메일 초안 TXT 다운로드",
                data=email_body,
                file_name="able_email_draft.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col_email_2:
            if st.button("SendGrid로 이메일 발송", use_container_width=True):
                with st.spinner("이메일 발송 중..."):
                    result = send_email(
                        to=recipient_email,
                        subject=email_subject,
                        body=email_body
                    )

                if result["status"] == "success":
                    st.success("이메일 발송 요청이 SendGrid에 접수되었습니다.")
                else:
                    st.error("이메일 발송 실패")
                    st.json(result)
    else:
        st.info("아직 이메일 초안이 없습니다.")

st.divider()
st.subheader("전체 결과 다운로드")

final_report = build_report_text()

if final_report.strip():
    st.download_button(
        label="전체 분석 결과 Markdown 다운로드",
        data=final_report,
        file_name="able_project_report.md",
        mime="text/markdown",
        use_container_width=True
    )
else:
    st.info("다운로드할 분석 결과가 없습니다.")
