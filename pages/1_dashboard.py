# -*- coding: utf-8 -*-
# pages/1_dashboard.py  — 회의 분석 대시보드
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import re
import requests
import streamlit as st
from datetime import datetime
from shared import (
    GLOBAL_CSS, ROLES, DEFAULT_MEETING_TEXT, OPENAI_API_KEY, SENDGRID_API_KEY, EMAIL_ADDRESS,
    render_sidebar, clear_results, extract_keywords, summarize_meeting, extract_tasks_ai,
    branding_insight, action_and_risk, decisions, ask_able, generate_notify_messages,
    make_email_draft, compare_meetings, extract_tasks_structured, add_tasks_to_state,
    fetch_related_news, transcribe_audio_file, render_tts_control, RESULT_KEYS,
)

st.set_page_config(
    page_title="에이블 · 회의 분석",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth guard ──
if not st.session_state.get("logged_in_user"):
    st.switch_page("app.py")

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
render_sidebar(current_page="1_dashboard.py")

user = st.session_state["logged_in_user"]
meta = ROLES[user]
color = meta["color"]

# ══════════════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="page-header">
    <div class="page-title">회의 분석 대시보드</div>
    <div class="page-subtitle" style="color:{color};">
        {meta['emoji']} {user} ({meta['title']}) · Z세대 리브랜딩 전략 AI 비서
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MEETING INPUT SECTION
# ══════════════════════════════════════════════════════════════
with st.container():
    st.markdown('''
    <div class="card">
        <div class="card-title" style="text-align:center;font-size:0.95rem;line-height:1.35;letter-spacing:0.04em;text-transform:none;color:#211A32;margin-bottom:0.65rem;">회의록 업로드 및 입력</div>
    ''', unsafe_allow_html=True)

    if "meeting_text" not in st.session_state:
        st.session_state["meeting_text"] = DEFAULT_MEETING_TEXT

    # File upload
    uploaded_file = st.file_uploader("파일 업로드 (txt / md)", type=["txt", "md"], label_visibility="collapsed")
    if uploaded_file:
        text_from_file = uploaded_file.read().decode("utf-8")
        if st.session_state.get("last_uploaded") != uploaded_file.name:
            st.session_state["meeting_text"] = text_from_file
            st.session_state["last_uploaded"] = uploaded_file.name
            clear_results()
            st.rerun()

    # STT는 회의록 입력 바로 위가 가장 자연스럽습니다.
    # 음성 회의/녹음 파일 → 텍스트 회의록 → 기존 분석 흐름으로 이어집니다.
    with st.expander("🎙️ 음성 입력 / STT", expanded=False):
        st.caption("마이크로 녹음하거나 음성 파일을 올리면 회의록 입력창에 텍스트로 반영됩니다.")
        audio_source = None
        if hasattr(st, "audio_input"):
            audio_source = st.audio_input("회의 음성 녹음", key="meeting_audio_input")
        else:
            audio_source = st.file_uploader("음성 파일 업로드 (wav / mp3 / m4a)", type=["wav", "mp3", "m4a", "webm"], key="meeting_audio_upload")

        stt_col1, stt_col2 = st.columns([1, 2])
        with stt_col1:
            if st.button("음성을 텍스트로 변환", key="btn_stt", use_container_width=True):
                if not audio_source:
                    st.warning("먼저 음성을 녹음하거나 파일을 업로드해주세요.")
                else:
                    with st.spinner("음성을 회의록으로 변환 중…"):
                        transcript = transcribe_audio_file(audio_source)
                    if transcript.strip():
                        st.session_state["meeting_text"] = transcript
                        clear_results()
                        st.success("STT 변환 완료! 입력창에 반영했습니다.")
                        st.rerun()
                    else:
                        st.warning("변환된 텍스트가 없습니다. 음성 파일을 다시 확인해주세요.")
        with stt_col2:
            st.caption("회의 분석 대시보드의 입력 영역에 넣는 것이 가장 효율적이라 이 위치에 배치했습니다.")

    col_ex, col_clear = st.columns([1, 1])
    with col_ex:
        if st.button("예시 회의록 불러오기", use_container_width=True):
            st.session_state["meeting_text"] = DEFAULT_MEETING_TEXT
            clear_results()
            st.rerun()
    with col_clear:
        if st.button("입력창 비우기", use_container_width=True):
            st.session_state["meeting_text"] = ""
            clear_results()
            st.rerun()

    meeting_text = st.text_area(
        "회의록",
        key="meeting_text",
        height=180,
        placeholder="회의록 내용을 붙여넣거나 위에서 파일을 업로드하세요.",
        label_visibility="collapsed",
    )
    st.markdown(f'<div style="font-size:0.72rem;color:#35334D;margin-top:4px;">{len(meeting_text):,}자</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Top action row: key actions aligned in one line ──
run_col, length_col, kw_btn_col, reset_col = st.columns([3.2, 2.1, 1.25, 1.25])
with run_col:
    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    run_all = st.button("⚡ 전체 분석 실행", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with length_col:
    length_opt = st.selectbox("요약 길이", ["보통", "짧게", "자세히"], label_visibility="collapsed")
with kw_btn_col:
    if st.button("🏷️ 키워드 추출", use_container_width=True):
        with st.spinner("키워드 추출 중..."):
            st.session_state["keywords_result"] = extract_keywords(meeting_text)
with reset_col:
    if st.button("↺ 초기화", use_container_width=True):
        clear_results()
        st.rerun()

if st.session_state.get("keywords_result"):
    tags_html = "".join([f'<span class="kw-tag"># {kw}</span>' for kw in st.session_state["keywords_result"]])
    st.markdown(f'<div class="kw-wrap">{tags_html}</div>', unsafe_allow_html=True)

if run_all:
    with st.spinner("에이블이 분석 중입니다…"):
        st.session_state["summary_result"]     = summarize_meeting(meeting_text, length_opt)
        st.session_state["tasks_result"]       = extract_tasks_ai(meeting_text)
        st.session_state["branding_result"]    = branding_insight(meeting_text)
        st.session_state["action_risk_result"] = action_and_risk(meeting_text)
        st.session_state["decisions_result"]   = decisions(meeting_text)
        # Also push tasks to dashboard
        extracted = extract_tasks_structured(meeting_text)
        if extracted:
            add_tasks_to_state(extracted)
    st.success(f"분석 완료! 업무 {len(extracted) if extracted else 0}개가 업무 대시보드에도 반영됐어요.")

# ── Snapshot / Compare ──
history = st.session_state.get("history", [])
snap_col, cmp_sel_col, cmp_btn_col = st.columns([3.2, 2.1, 2.5])
with snap_col:
    if st.button("💾 스냅샷 저장", use_container_width=True):
        if "history" not in st.session_state:
            st.session_state["history"] = []
        st.session_state["history"].append({
            "saved_at": datetime.now().strftime("%m/%d %H:%M"),
            "text": meeting_text,
            "results": {k: st.session_state.get(k, "") for k in RESULT_KEYS},
        })
        st.success(f"스냅샷 #{len(st.session_state['history'])} 저장 완료!")

if len(history) >= 1:
    with cmp_sel_col:
        snap_opts = [f"#{i+1} · {s['saved_at']}" for i, s in enumerate(history)]
        sel = st.selectbox("비교할 스냅샷", snap_opts, label_visibility="collapsed")
    with cmp_btn_col:
        if st.button("🔍 이전 회의 대비 변화 분석", use_container_width=True):
            idx = snap_opts.index(sel)
            with st.spinner("변화 분석 중..."):
                st.session_state["compare_result"] = compare_meetings(history[idx]["text"], meeting_text)
else:
    with cmp_sel_col:
        st.caption("스냅샷을 먼저 저장하면")
    with cmp_btn_col:
        st.caption("회의 간 비교가 가능해요.")

if st.session_state.get("compare_result"):
    with st.expander("📊 이전 회의 대비 변화 분석", expanded=True):
        st.markdown(st.session_state["compare_result"])

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# RESULT TABS
# ══════════════════════════════════════════════════════════════
access = meta.get("access", "full")

# Decide which tabs are visible
all_tabs = ["📋 회의 요약", "✅ 담당자 과제", "💡 리브랜딩 인사이트", "⚙️ 실행·리스크", "🔒 결정사항", "🤖 에이블 Q&A", "📧 이메일", "🔔 알림 메시지", "📰 관련 뉴스"]
tab_access = {
    "full":      [0, 1, 2, 3, 4, 5, 6, 7, 8],
    "strategy":  [0, 1, 3, 4, 5, 7, 8],
    "shortform": [0, 1, 2, 5, 8],
}
allowed = tab_access.get(access, [0, 1, 2, 3, 4, 5, 6, 7, 8])
visible_tabs = [(i, label) for i, label in enumerate(all_tabs) if i in allowed]

tab_objects = st.tabs([label for _, label in visible_tabs])

def tab_for(index):
    """Return tab object matching original tab index, or None."""
    for pos, (orig_i, _) in enumerate(visible_tabs):
        if orig_i == index:
            return tab_objects[pos]
    return None

# ── 0: 회의 요약 ──
t = tab_for(0)
if t:
    with t:
        col_l, col_r = st.columns([3, 1])
        with col_r:
            sum_len = st.selectbox("길이", ["보통", "짧게", "자세히"], key="sum_len_tab")
        with col_l:
            if st.button("요약 생성", key="btn_summary"):
                with st.spinner("생성 중..."):
                    st.session_state["summary_result"] = summarize_meeting(meeting_text, sum_len)
        if st.session_state.get("summary_result"):
            st.markdown(st.session_state["summary_result"])
            render_tts_control(st.session_state["summary_result"], "tts_summary")
        else:
            st.info("⚡ 전체 분석 실행 또는 요약 생성 버튼을 눌러주세요.")

# ── 1: 담당자 과제 ──
t = tab_for(1)
if t:
    with t:
        view_mode = st.radio("보기 모드", ["📊 표 보기", "☑️ 체크리스트"], horizontal=True)
        if st.button("과제 추출", key="btn_tasks"):
            with st.spinner("생성 중..."):
                st.session_state["tasks_result"] = extract_tasks_ai(meeting_text)
                st.session_state.pop("todo_checks", None)
        if st.session_state.get("tasks_result"):
            if view_mode == "📊 표 보기":
                st.markdown(st.session_state["tasks_result"])
                render_tts_control(st.session_state["tasks_result"], "tts_tasks")
            else:
                # parse to checklist
                rows = []
                lines = st.session_state["tasks_result"].strip().split("\n")
                header_passed = False
                for line in lines:
                    if not line.startswith("|"): continue
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    if "---" in cells[0]: header_passed = True; continue
                    if not header_passed: continue
                    if len(cells) >= 2 and cells[0] and cells[1]:
                        rows.append({"담당자": cells[0], "업무": cells[1],
                            "마감일": cells[3] if len(cells) > 3 else "-",
                            "우선순위": cells[4] if len(cells) > 4 else "-"})
                if not rows:
                    st.markdown(st.session_state["tasks_result"])
                    render_tts_control(st.session_state["tasks_result"], "tts_tasks")
                else:
                    if "todo_checks" not in st.session_state:
                        st.session_state["todo_checks"] = {i: False for i in range(len(rows))}
                    done = sum(st.session_state["todo_checks"].values())
                    pct = int(done / len(rows) * 100) if rows else 0
                    st.markdown(f"**완료율 {done}/{len(rows)} ({pct}%)**")
                    st.markdown(f'<div class="prog-wrap"><div class="prog-fill" style="width:{pct}%;"></div></div>', unsafe_allow_html=True)
                    by_person = {}
                    for i, row in enumerate(rows):
                        by_person.setdefault(row["담당자"], []).append((i, row))
                    for person, items in by_person.items():
                        p_done = sum(st.session_state["todo_checks"].get(i, False) for i, _ in items)
                        st.markdown(f"**{person}** ({p_done}/{len(items)})")
                        for idx, row in items:
                            checked = st.checkbox(
                                f"{row['업무']}  ·  마감: {row['마감일']}  ·  우선순위: {row['우선순위']}",
                                value=st.session_state["todo_checks"].get(idx, False),
                                key=f"todo_{idx}"
                            )
                            st.session_state["todo_checks"][idx] = checked
        else:
            st.info("과제 추출 버튼을 눌러주세요.")

# ── 2: 리브랜딩 인사이트 ──
t = tab_for(2)
if t:
    with t:
        if st.button("인사이트 생성", key="btn_branding"):
            with st.spinner("생성 중..."):
                st.session_state["branding_result"] = branding_insight(meeting_text)
        if st.session_state.get("branding_result"):
            st.markdown(st.session_state["branding_result"])
            render_tts_control(st.session_state["branding_result"], "tts_branding")
        else:
            st.info("인사이트 생성 버튼을 눌러주세요.")

# ── 3: 실행·리스크 ──
t = tab_for(3)
if t:
    with t:
        if st.button("생성", key="btn_action"):
            with st.spinner("생성 중..."):
                st.session_state["action_risk_result"] = action_and_risk(meeting_text)
        if st.session_state.get("action_risk_result"):
            st.markdown(st.session_state["action_risk_result"])
            render_tts_control(st.session_state["action_risk_result"], "tts_action")
        else:
            st.info("생성 버튼을 눌러주세요.")

# ── 4: 결정사항 ──
t = tab_for(4)
if t:
    with t:
        if st.button("추출", key="btn_decisions"):
            with st.spinner("생성 중..."):
                st.session_state["decisions_result"] = decisions(meeting_text)
        if st.session_state.get("decisions_result"):
            st.markdown(st.session_state["decisions_result"])
            render_tts_control(st.session_state["decisions_result"], "tts_decisions")
        else:
            st.info("추출 버튼을 눌러주세요.")

# ── 5: Q&A ──
t = tab_for(5)
if t:
    with t:
        question = st.text_input("질문 입력", placeholder="에이블에게 질문하기", label_visibility="collapsed")
        if st.button("질문하기", key="btn_qa"):
            with st.spinner("답변 생성 중..."):
                ref = meeting_text + "\n\n" + "\n\n".join(
                    [st.session_state.get(k, "") for k in RESULT_KEYS if st.session_state.get(k)])
                st.session_state["qa_result"] = ask_able(question, ref)
        if st.session_state.get("qa_result"):
            st.markdown(st.session_state["qa_result"])
            render_tts_control(st.session_state["qa_result"], "tts_qa")
        else:
            st.info("질문을 입력하고 버튼을 눌러주세요.")

# ── 6: 이메일 ──
t = tab_for(6)
if t:
    with t:
        e1, e2 = st.columns(2)
        with e1:
            r_name  = st.text_input("수신자명", value="팀장님")
            r_email = st.text_input("수신자 이메일", value="")
        with e2:
            s_name  = st.text_input("발신자명", value="에이블")
            subject = st.text_input("이메일 제목", value="[에이블 브리핑] 회의 정리")
        if st.button("이메일 초안 생성", key="btn_email"):
            with st.spinner("초안 생성 중..."):
                st.session_state["email_draft_result"] = make_email_draft(meeting_text, r_name, s_name)
        if st.session_state.get("email_draft_result"):
            body = st.text_area("이메일 본문", value=st.session_state["email_draft_result"], height=360)
            dl_col, send_col = st.columns(2)
            with dl_col:
                st.download_button("⬇ TXT 다운로드", data=body,
                    file_name="able_email.txt", mime="text/plain", use_container_width=True)
            with send_col:
                if st.button("SendGrid 발송", use_container_width=True):
                    if not SENDGRID_API_KEY:
                        st.error("SENDGRID_API_KEY가 없습니다.")
                    elif "@" not in (r_email or ""):
                        st.error("이메일 주소를 확인해주세요.")
                    else:
                        with st.spinner("발송 중..."):
                            headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
                            payload = {
                                "personalizations": [{"to": [{"email": r_email}], "subject": subject}],
                                "from": {"email": EMAIL_ADDRESS},
                                "content": [{"type": "text/plain", "value": body}],
                            }
                            resp = requests.post("https://api.sendgrid.com/v3/mail/send",
                                headers=headers, json=payload, timeout=20)
                            if resp.status_code == 202:
                                st.success("발송 완료!")
                            else:
                                st.error(f"발송 실패: {resp.text}")
        else:
            st.info("초안 생성 버튼을 눌러주세요.")

# ── 7: 알림 메시지 ──
t = tab_for(7)
if t:
    with t:
        if st.button("알림 메시지 생성", key="btn_notify", use_container_width=True):
            with st.spinner("메시지 생성 중..."):
                st.session_state["notify_result"] = generate_notify_messages(meeting_text)
        if st.session_state.get("notify_result"):
            raw = st.session_state["notify_result"]
            blocks = re.split(r"(?=##\s)", raw.strip())
            for block in blocks:
                if not block.strip(): continue
                lines = block.strip().split("\n")
                title = lines[0].replace("##", "").strip()
                body  = "\n".join(lines[1:]).strip().lstrip("-").strip()
                st.markdown(
                    f'<div class="n-card"><div class="n-card-title">📣 {title}</div>'
                    f'<div class="n-card-body">{body.replace(chr(10), "<br>")}</div></div>',
                    unsafe_allow_html=True,
                )
            st.download_button("⬇ 알림 TXT 다운로드", data=raw,
                file_name="able_notify.txt", mime="text/plain", use_container_width=True)
            render_tts_control(raw, "tts_notify")
        else:
            st.info("알림 메시지 생성 버튼을 눌러주세요.")


# ── 8: 관련 뉴스 ──
t = tab_for(8)
if t:
    with t:
        st.markdown("#### 관련 트렌드 뉴스")
        st.caption("회의 주제와 관련된 마케팅 / Z세대 / 숏폼 트렌드 뉴스 5건을 AI가 요약합니다.")

        news_kw = st.text_input(
            "검색 키워드 (선택)",
            placeholder="예: Z세대 리브랜딩, 숏폼 바이럴 — 비워두면 회의 내용 기반으로 자동 검색",
            key="dash_news_kw",
        )
        if st.button("뉴스 가져오기", key="btn_dash_news", use_container_width=False):
            with st.spinner("뉴스 요약 중…"):
                st.session_state["news_result"] = fetch_related_news(meeting_text, news_kw)

        if st.session_state.get("news_result"):
            articles = st.session_state["news_result"]
            if not articles:
                st.warning("뉴스를 가져오지 못했습니다. 다시 시도해주세요.")
            else:
                for i, art in enumerate(articles, 1):
                    st.markdown(
                        f'<div class="n-card">'
                        f'<div class="news-source">기사 {i} · {art.get("source","")} · {art.get("date","")}</div>'
                        f'<div class="news-title">{art.get("title","")}</div>'
                        f'<div class="news-body">{art.get("summary","")}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                news_text = "\n\n".join([
                    f"[{i}] {a.get('title','')} ({a.get('source','')} / {a.get('date','')})\n{a.get('summary','')}"
                    for i, a in enumerate(articles, 1)
                ])
                st.download_button("⬇ 뉴스 TXT 다운로드", data=news_text,
                    file_name="able_news.txt", mime="text/plain", use_container_width=True)
                render_tts_control(news_text, "tts_news")
        else:
            st.info("뉴스 가져오기 버튼을 눌러주세요.")

# ══════════════════════════════════════════════════════════════
# DOWNLOAD ALL
# ══════════════════════════════════════════════════════════════
st.markdown("---")
section_map = [
    ("# 회의 요약", "summary_result"), ("# 담당자 과제", "tasks_result"),
    ("# 리브랜딩 인사이트", "branding_result"), ("# 실행·리스크", "action_risk_result"),
    ("# 결정사항", "decisions_result"), ("# Q&A", "qa_result"),
    ("# 알림 메시지", "notify_result"), ("# 이메일 초안", "email_draft_result"),
    ("# 관련 뉴스", "news_result"),
]
report = "\n\n".join([f"{h}\n\n{st.session_state[k]}" for h, k in section_map if st.session_state.get(k)])
if report.strip():
    st.download_button("⬇ 전체 분석 결과 Markdown 다운로드", data=report,
        file_name="able_report.md", mime="text/markdown", use_container_width=True)
