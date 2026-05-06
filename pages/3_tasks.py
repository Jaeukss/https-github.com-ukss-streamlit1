# -*- coding: utf-8 -*-
# pages/3_tasks.py  — 업무 대시보드
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pandas as pd
import streamlit as st
from shared import (
    GLOBAL_CSS, ROLES,
    render_sidebar, extract_tasks_structured, add_tasks_to_state,
)

st.set_page_config(
    page_title="에이블 · 업무 대시보드",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not st.session_state.get("logged_in_user"):
    st.switch_page("app.py")

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Extra CSS specific to tasks page ──
st.markdown("""
<style>
.metric-row { display: flex; gap: 12px; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-box {
    background: #13121E; border: 1px solid #1E1C2E; border-radius: 12px;
    padding: 0.9rem 1.2rem; min-width: 110px; flex: 1;
    text-align: center;
}
.metric-val { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: #E8E5F5; }
.metric-lbl { font-size: 0.72rem; color: #4E4B63; margin-top: 2px; font-weight: 600; letter-spacing: 0.06em; }

.task-card {
    background: #13121E; border: 1px solid #1E1C2E; border-radius: 14px;
    padding: 1.1rem 1.3rem; margin-bottom: 0.6rem; height: 100%;
}
.tc-priority { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.4rem; }
.tc-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #E8E5F5; margin-bottom: 0.4rem; }
.tc-desc { font-size: 0.78rem; color: #6B6680; line-height: 1.55; margin-bottom: 0.7rem; }
.tc-meta { font-size: 0.72rem; color: #4E4B63; }
.badge {
    display: inline-block; border-radius: 20px; padding: 2px 10px;
    font-size: 0.68rem; font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

render_sidebar(current_page="3_tasks.py")

user = st.session_state["logged_in_user"]
meta = ROLES[user]
color = meta["color"]

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
STATUS_FLOW = {"진행 예정": "진행 중", "진행 중": "검토 중", "검토 중": "완료"}

def priority_style(p):
    return {
        "높음":  ("color:#FF6B6B;", "🔴"),
        "보통":  ("color:#FFD93D;", "🟡"),
        "낮음":  ("color:#6BCB77;", "🟢"),
    }.get(p, ("color:#4E4B63;", "⚪"))

def status_color(s):
    return {
        "진행 예정": "#4E4B63",
        "진행 중":   "#BFA8FF",
        "검토 중":   "#60C8F5",
        "완료":      "#5ADBA9",
    }.get(s, "#4E4B63")

def move_status(task_id):
    for t in st.session_state["tasks"]:
        if t.get("task_id") == task_id:
            curr = t.get("status", "진행 예정")
            t["status"] = STATUS_FLOW.get(curr, curr)
            break

# ══════════════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="page-header">
    <div class="page-title">업무 대시보드</div>
    <div class="page-subtitle" style="color:{color};">
        {meta['emoji']} {user} · 회의록에서 자동 추출된 업무를 관리합니다
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# UPLOAD & EXTRACT
# ══════════════════════════════════════════════════════════════
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

with st.expander("📁 회의록에서 업무 추출하기", expanded=not bool(st.session_state["tasks"])):
    # Pull from existing meeting text if available
    existing = st.session_state.get("meeting_text", "")
    up_col, txt_col = st.columns([1, 2])
    with up_col:
        uploaded = st.file_uploader("회의록 파일 업로드 (txt)", type=["txt"], label_visibility="collapsed")
    with txt_col:
        if st.button("현재 회의록에서 업무 추출", use_container_width=True, key="extract_from_session"):
            if existing.strip():
                with st.spinner("업무 추출 중…"):
                    new_tasks = extract_tasks_structured(existing)
                    added = add_tasks_to_state(new_tasks)
                st.success(f"{added}개 업무가 추가됐습니다!")
                st.rerun()
            else:
                st.warning("회의 분석 대시보드에서 회의록을 먼저 입력해주세요.")

    if uploaded:
        minutes_text = uploaded.read().decode("utf-8")
        if st.session_state.get("last_task_upload") != uploaded.name:
            st.session_state["last_task_upload"] = uploaded.name
            with st.spinner("업무 추출 중…"):
                new_tasks = extract_tasks_structured(minutes_text)
                added = add_tasks_to_state(new_tasks)
            st.success(f"파일에서 {added}개 업무가 추가됐습니다!")
            st.rerun()

tasks = st.session_state["tasks"]

# ══════════════════════════════════════════════════════════════
# EMPTY STATE
# ══════════════════════════════════════════════════════════════
if not tasks:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;background:#13121E;border:1px dashed #1E1C2E;border-radius:14px;margin-top:1rem;">
        <div style="font-size:2.5rem;margin-bottom:0.7rem;">📭</div>
        <div style="color:#4E4B63;font-size:0.9rem;font-weight:600;">등록된 업무가 없습니다.<br>위에서 회의록을 업로드하거나 업무를 추출해주세요.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════
# SUMMARY METRICS
# ══════════════════════════════════════════════════════════════
df_all = pd.DataFrame(tasks)
for col in ["task_id","title","description","assignee","priority","due_date","status"]:
    if col not in df_all.columns:
        df_all[col] = ""

total   = len(df_all)
todo    = len(df_all[df_all["status"] == "진행 예정"])
doing   = len(df_all[df_all["status"] == "진행 중"])
review  = len(df_all[df_all["status"] == "검토 중"])
done    = len(df_all[df_all["status"] == "완료"])
high_p  = len(df_all[df_all["priority"] == "높음"])
pct_done = int(done / total * 100) if total else 0

st.markdown(f"""
<div class="metric-row">
    <div class="metric-box"><div class="metric-val">{total}</div><div class="metric-lbl">전체 업무</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#4E4B63;">{todo}</div><div class="metric-lbl">진행 예정</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#BFA8FF;">{doing}</div><div class="metric-lbl">진행 중</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#60C8F5;">{review}</div><div class="metric-lbl">검토 중</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#5ADBA9;">{done}</div><div class="metric-lbl">완료</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#FF6B6B;">{high_p}</div><div class="metric-lbl">높은 우선순위</div></div>
    <div class="metric-box"><div class="metric-val">{pct_done}%</div><div class="metric-lbl">완료율</div></div>
</div>
<div style="background:#1A182A;border-radius:6px;height:8px;overflow:hidden;margin-bottom:1.5rem;">
    <div style="background:linear-gradient(90deg,#BFA8FF,#5ADBA9);height:100%;border-radius:6px;width:{pct_done}%;transition:width 0.4s;"></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TWO VIEWS: 편집 테이블 | 카드 보기
# ══════════════════════════════════════════════════════════════
view_tab1, view_tab2 = st.tabs(["📊 편집 테이블", "🗂️ 카드 보기"])

# ── 편집 테이블 ──
with view_tab1:
    st.caption("상태·담당자·마감일·우선순위를 직접 수정할 수 있습니다. 수정 후 저장 버튼을 눌러주세요.")

    df_edit = df_all[["task_id","title","description","assignee","priority","due_date","status"]].copy()

    edited = st.data_editor(
        df_edit,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "task_id":     st.column_config.NumberColumn("ID", disabled=True),
            "title":       st.column_config.TextColumn("업무명", required=True),
            "description": st.column_config.TextColumn("업무 설명"),
            "assignee":    st.column_config.TextColumn("담당자"),
            "priority":    st.column_config.SelectboxColumn("우선순위", options=["높음","보통","낮음"], required=True),
            "due_date":    st.column_config.TextColumn("마감일", help="예: 2026-05-10 또는 미정"),
            "status":      st.column_config.SelectboxColumn("상태", options=["진행 예정","진행 중","검토 중","완료"], required=True),
        },
    )

    save_col, reset_col, _ = st.columns([1, 1, 4])
    with save_col:
        if st.button("💾 수정사항 저장", use_container_width=True):
            st.session_state["tasks"] = edited.to_dict("records")
            st.success("저장됐습니다!")
            st.rerun()
    with reset_col:
        if st.button("🗑️ 전체 삭제", use_container_width=True):
            st.session_state["tasks"] = []
            st.rerun()

# ── 카드 보기 ──
with view_tab2:
    status_opts = ["전체", "진행 예정", "진행 중", "검토 중", "완료"]
    selected_status = st.radio("상태 필터", status_opts, horizontal=True)

    filtered = df_all if selected_status == "전체" else df_all[df_all["status"] == selected_status]
    st.markdown(f'<div style="font-size:0.78rem;color:#4E4B63;margin-bottom:0.8rem;">총 {len(filtered)}개</div>', unsafe_allow_html=True)

    if filtered.empty:
        st.info("해당 상태의 업무가 없습니다.")
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered.iterrows()):
            pstyle, picon = priority_style(row.get("priority",""))
            sc = status_color(row.get("status",""))
            with cols[i % 3]:
                st.markdown(f"""
                <div class="task-card">
                    <div class="tc-priority" style="{pstyle}">{picon} 우선순위 {row.get('priority','')}</div>
                    <div class="tc-title">{row.get('title','')}</div>
                    <div class="tc-desc">{row.get('description','—')}</div>
                    <div class="tc-meta">👤 {row.get('assignee','미정')} &nbsp;·&nbsp; 📅 {row.get('due_date','미정')}</div>
                    <div style="margin-top:0.6rem;">
                        <span class="badge" style="background:{sc}1A;color:{sc};border:1px solid {sc}44;">
                            {row.get('status','')}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                tid = row.get("task_id")
                if row.get("status") != "완료":
                    next_s = STATUS_FLOW.get(row.get("status",""), "")
                    if st.button(f"→ {next_s}", key=f"move_{tid}_{i}", use_container_width=True):
                        move_status(tid)
                        st.rerun()
