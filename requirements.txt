# -*- coding: utf-8 -*-
# pages/3_tasks.py  — 업무 대시보드
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pandas as pd
import streamlit as st
from shared import (
    GLOBAL_CSS, ROLES,
    render_sidebar, extract_tasks_structured, add_tasks_to_state, render_tts_control,
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
    background: #FFFFFF; border: 1px solid #E5DDF7; border-radius: 12px;
    padding: 0.9rem 1.2rem; min-width: 110px; flex: 1;
    text-align: center;
}
.metric-val { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: #211A32; }
.metric-lbl { font-size: 0.72rem; color: #6F6682; margin-top: 2px; font-weight: 600; letter-spacing: 0.06em; }

.task-card {
    background: #FFFFFF; border: 1px solid #E5DDF7; border-radius: 14px;
    padding: 1.1rem 1.3rem; margin-bottom: 0.6rem; height: 100%;
}
.tc-priority { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.4rem; }
.tc-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #211A32; margin-bottom: 0.4rem; }
.tc-desc { font-size: 0.78rem; color: #766D8A; line-height: 1.55; margin-bottom: 0.7rem; }
.tc-meta { font-size: 0.72rem; color: #6F6682; }
.badge {
    display: inline-block; border-radius: 20px; padding: 2px 10px;
    font-size: 0.68rem; font-weight: 700;
}
.flow-grid { display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap:12px; margin-top:0.8rem; }
.flow-col { background:#FFFFFF; border:1px solid #E5DDF7; border-radius:14px; padding:0.95rem; min-height:180px; }
.flow-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem; }
.flow-title { font-size:0.82rem; font-weight:800; color:#211A32; }
.flow-count { font-size:0.7rem; font-weight:800; color:#7C5CFF; background:#F1ECFF; border:1px solid #DED2FF; border-radius:999px; padding:2px 8px; }
.flow-item { background:#FAF8FF; border:1px solid #ECE6FB; border-radius:12px; padding:0.75rem 0.8rem; margin-bottom:0.55rem; }
.flow-item-title { font-size:0.8rem; font-weight:800; color:#211A32; line-height:1.4; }
.flow-item-meta { font-size:0.7rem; color:#6F6682; margin-top:0.35rem; line-height:1.5; }
.person-flow { background:#FFFFFF; border:1px solid #E5DDF7; border-radius:14px; padding:1rem 1.1rem; margin-bottom:0.65rem; }
.person-top { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:0.55rem; }
.person-name { font-size:0.86rem; font-weight:800; color:#211A32; }
.person-stats { font-size:0.72rem; color:#6F6682; }
.flow-progress { background:#F1ECFF; border-radius:999px; height:8px; overflow:hidden; }
.flow-progress-fill { background:linear-gradient(90deg,#7C5CFF,#17A976); height:100%; border-radius:999px; }
.next-action { background:#FFFFFF; border:1px solid #E5DDF7; border-radius:14px; padding:1rem 1.1rem; margin-bottom:0.7rem; color:#211A32; }
.next-action strong { color:#7C5CFF; }
@media (max-width: 900px) { .flow-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px) { .flow-grid { grid-template-columns: 1fr; } }
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
        "높음":  ("color:#D9364B;", "🔴"),
        "보통":  ("color:#B68A00;", "🟡"),
        "낮음":  ("color:#219653;", "🟢"),
    }.get(p, ("color:#6F6682;", "⚪"))

def status_color(s):
    return {
        "진행 예정": "#6F6682",
        "진행 중":   "#7C5CFF",
        "검토 중":   "#2496D8",
        "완료":      "#17A976",
    }.get(s, "#6F6682")

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
    <div style="text-align:center;padding:1.8rem 2rem;background:#FFFFFF;border:1px dashed #E5DDF7;border-radius:14px;margin:1rem 0;">
        <div style="font-size:2.1rem;margin-bottom:0.5rem;">📭</div>
        <div style="color:#6F6682;font-size:0.9rem;font-weight:600;">등록된 업무가 없습니다.<br>아래 탭은 바로 확인 가능하며, 위에서 회의록을 업로드하거나 업무를 추출하면 업무 흐름에 자동 반영됩니다.</div>
    </div>
    """, unsafe_allow_html=True)

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
    <div class="metric-box"><div class="metric-val" style="color:#6F6682;">{todo}</div><div class="metric-lbl">진행 예정</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#7C5CFF;">{doing}</div><div class="metric-lbl">진행 중</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#2496D8;">{review}</div><div class="metric-lbl">검토 중</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#17A976;">{done}</div><div class="metric-lbl">완료</div></div>
    <div class="metric-box"><div class="metric-val" style="color:#D9364B;">{high_p}</div><div class="metric-lbl">높은 우선순위</div></div>
    <div class="metric-box"><div class="metric-val">{pct_done}%</div><div class="metric-lbl">완료율</div></div>
</div>
<div style="background:#F1ECFF;border-radius:6px;height:8px;overflow:hidden;margin-bottom:1.5rem;">
    <div style="background:linear-gradient(90deg,#7C5CFF,#17A976);height:100%;border-radius:6px;width:{pct_done}%;transition:width 0.4s;"></div>
</div>
""", unsafe_allow_html=True)

status_summary_text = (
    f"업무 현황입니다. 전체 업무는 {total}개이고, 진행 예정 {todo}개, 진행 중 {doing}개, "
    f"검토 중 {review}개, 완료 {done}개입니다. 완료율은 {pct_done}퍼센트입니다. "
    f"높은 우선순위 업무는 {high_p}개입니다."
)
render_tts_control(status_summary_text, "tts_task_status", label="🔊 업무 현황 음성으로 듣기")

# ══════════════════════════════════════════════════════════════
# THREE VIEWS: 편집 테이블 | 카드 보기 | 업무 흐름
# ══════════════════════════════════════════════════════════════
st.markdown('<div style="font-size:0.78rem;color:#6F6682;margin-bottom:0.4rem;">업무 표·카드·흐름을 같은 데이터로 확인합니다.</div>', unsafe_allow_html=True)
view_tab1, view_tab2, view_tab3 = st.tabs(["📊 편집 테이블", "🗂️ 카드 보기", "🔄 업무 흐름"])

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
    st.markdown(f'<div style="font-size:0.78rem;color:#6F6682;margin-bottom:0.8rem;">총 {len(filtered)}개</div>', unsafe_allow_html=True)

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

# ── 업무 흐름 ──
with view_tab3:
    st.caption("업무가 진행 예정 → 진행 중 → 검토 중 → 완료로 어떻게 흘러가는지 한눈에 확인합니다.")

    flow_statuses = ["진행 예정", "진행 중", "검토 중", "완료"]
    st.markdown('<div class="flow-grid">', unsafe_allow_html=True)
    for status in flow_statuses:
        sub = df_all[df_all["status"] == status]
        sc = status_color(status)
        st.markdown(
            f'<div class="flow-col">'
            f'<div class="flow-head"><div class="flow-title" style="color:{sc};">{status}</div><div class="flow-count">{len(sub)}</div></div>',
            unsafe_allow_html=True,
        )
        if sub.empty:
            st.markdown('<div style="font-size:0.76rem;color:#9A90AD;padding:0.4rem 0;">해당 업무 없음</div>', unsafe_allow_html=True)
        else:
            for _, row in sub.head(6).iterrows():
                pstyle, picon = priority_style(row.get("priority", ""))
                st.markdown(
                    f'<div class="flow-item">'
                    f'<div class="flow-item-title">{row.get("title", "")}</div>'
                    f'<div class="flow-item-meta">👤 {row.get("assignee", "미정")} · 📅 {row.get("due_date", "미정")}<br>'
                    f'<span style="{pstyle}">{picon} {row.get("priority", "")}</span></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            if len(sub) > 6:
                st.markdown(f'<div style="font-size:0.72rem;color:#6F6682;">외 {len(sub)-6}개 더 있음</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### 담당자별 진행 흐름")
    assignee_df = df_all.copy()
    assignee_df["assignee"] = assignee_df["assignee"].replace("", "미정").fillna("미정")
    for assignee, group in assignee_df.groupby("assignee", dropna=False):
        g_total = len(group)
        g_done = len(group[group["status"] == "완료"])
        g_doing = len(group[group["status"] == "진행 중"])
        g_review = len(group[group["status"] == "검토 중"])
        g_todo = len(group[group["status"] == "진행 예정"])
        g_pct = int(g_done / g_total * 100) if g_total else 0
        st.markdown(
            f'<div class="person-flow">'
            f'<div class="person-top"><div class="person-name">👤 {assignee}</div>'
            f'<div class="person-stats">진행 예정 {g_todo} · 진행 중 {g_doing} · 검토 중 {g_review} · 완료 {g_done}</div></div>'
            f'<div class="flow-progress"><div class="flow-progress-fill" style="width:{g_pct}%;"></div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### 다음 액션 추천")
    recommendations = []
    if high_p and len(df_all[(df_all["priority"] == "높음") & (df_all["status"] == "진행 예정")]) > 0:
        recommendations.append("<strong>높은 우선순위</strong>인데 아직 진행 예정인 업무가 있습니다. 먼저 착수할 항목을 정해보세요.")
    if review >= 3:
        recommendations.append("<strong>검토 중</strong> 업무가 3개 이상입니다. 의사결정자 확인이 지연되고 있는지 점검해보세요.")
    if doing == 0 and todo > 0:
        recommendations.append("진행 중인 업무가 없습니다. 오늘 바로 시작할 업무를 1~2개 지정하면 흐름이 살아납니다.")
    if pct_done >= 70:
        recommendations.append("완료율이 높습니다. 남은 검토/마무리 업무를 정리하면 프로젝트 종료 단계로 넘어갈 수 있습니다.")
    if not recommendations:
        recommendations.append("현재 업무 흐름이 안정적입니다. 진행 중 업무의 마감일과 담당자만 주기적으로 확인하세요.")

    for rec in recommendations:
        st.markdown(f'<div class="next-action">💡 {rec}</div>', unsafe_allow_html=True)

    workflow_tts = (
        f"업무 흐름 요약입니다. 진행 예정 {todo}개, 진행 중 {doing}개, 검토 중 {review}개, 완료 {done}개입니다. "
        + " ".join([r.replace("<strong>", "").replace("</strong>", "") for r in recommendations])
    )
    render_tts_control(workflow_tts, "tts_task_workflow", label="🔊 업무 흐름 음성으로 듣기")

