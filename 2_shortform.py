# -*- coding: utf-8 -*-
# pages/2_shortform.py  — 숏폼 스튜디오
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from shared import (
    GLOBAL_CSS, ROLES,
    render_sidebar,
    shortform_strategy, generate_shortform_script, generate_ab_test, fetch_related_news,
)

st.set_page_config(
    page_title="에이블 · 숏폼 스튜디오",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not st.session_state.get("logged_in_user"):
    st.switch_page("app.py")

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
render_sidebar(current_page="2_shortform.py")

user = st.session_state["logged_in_user"]
meta = ROLES[user]
color = meta["color"]
access = meta.get("access", "full")

# ── Access guard: only full / shortform roles ──
if access == "strategy":
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">숏폼 스튜디오</div>
    </div>
    <div style="background:#13121E;border:1px dashed #2E2B48;border-radius:14px;padding:3rem 2rem;text-align:center;margin-top:1rem;">
        <div style="font-size:2.5rem;margin-bottom:0.7rem;">🔒</div>
        <div style="color:#6B6680;font-size:0.9rem;font-weight:600;">이 페이지는 접근 권한이 없습니다.<br>담당자에게 문의해주세요.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="page-header">
    <div class="page-title">숏폼 스튜디오</div>
    <div class="page-subtitle" style="color:{color};">
        {meta['emoji']} {user} · 숏폼 전략 · 스크립트 · A/B 테스트 · 뉴스
    </div>
</div>
""", unsafe_allow_html=True)

# ── Reference meeting text (read-only pull from session) ──
meeting_text = st.session_state.get("meeting_text", "")
if not meeting_text.strip():
    st.warning("회의 분석 대시보드에서 회의록을 먼저 입력해주세요. 여기서 직접 입력하려면 아래 박스를 사용하세요.")

with st.expander("📝 참고 회의록 (직접 입력 / 수정 가능)", expanded=not bool(meeting_text.strip())):
    meeting_text = st.text_area(
        "회의록",
        value=meeting_text,
        height=150,
        label_visibility="collapsed",
        key="sf_meeting_ref",
        placeholder="숏폼 전략의 기반이 될 회의록을 입력하세요.",
    )
    if st.button("이 내용으로 저장", key="sf_save_ref"):
        st.session_state["meeting_text"] = meeting_text
        st.success("저장됐어요!")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# FOUR TABS
# ══════════════════════════════════════════════════════════════
tab_strategy, tab_script, tab_ab, tab_news = st.tabs([
    "🎬 숏폼 전략", "🎥 스크립트 생성", "🔀 A/B 테스트", "📰 관련 뉴스",
])

# ── 숏폼 전략 ──
with tab_strategy:
    st.markdown("#### 숏폼 확산 전략")
    st.caption("회의 내용 기반으로 플랫폼별 전략, 챌린지 아이디어, 인플루언서 협업 방향을 도출합니다.")

    if st.button("전략 생성", key="btn_sf_strategy", use_container_width=False):
        with st.spinner("전략 생성 중…"):
            st.session_state["shortform_result"] = shortform_strategy(meeting_text)

    if st.session_state.get("shortform_result"):
        st.markdown(st.session_state["shortform_result"])
        st.download_button("⬇ 전략 TXT 다운로드",
            data=st.session_state["shortform_result"],
            file_name="able_sf_strategy.txt", mime="text/plain")
    else:
        st.info("전략 생성 버튼을 눌러주세요.")

# ── 스크립트 생성 ──
with tab_script:
    st.markdown("#### 60초 숏폼 스크립트")
    st.caption("Hook → 전개 → CTA 구조로 실제 촬영 가능한 스크립트를 생성합니다.")

    concept_hint = st.text_input(
        "컨셉 힌트 (선택)",
        placeholder="예: 브랜드 레거시를 반전시키는 챌린지, Z세대 감성으로 제품 재해석",
        key="sf_concept",
    )
    if st.button("스크립트 생성", key="btn_sf_script", use_container_width=False):
        with st.spinner("스크립트 생성 중…"):
            st.session_state["script_result"] = generate_shortform_script(meeting_text, concept_hint)

    if st.session_state.get("script_result"):
        st.markdown(st.session_state["script_result"])
        st.download_button("⬇ 스크립트 TXT 다운로드",
            data=st.session_state["script_result"],
            file_name="able_script.txt", mime="text/plain")
    else:
        st.info("스크립트 생성 버튼을 눌러주세요.")

# ── A/B 테스트 ──
with tab_ab:
    st.markdown("#### A/B 테스트 아이디어")
    st.caption("숏폼 콘텐츠의 A/B 테스트 시나리오 3세트를 자동 생성합니다.")

    if st.button("A/B 테스트 아이디어 생성", key="btn_ab", use_container_width=False):
        with st.spinner("생성 중…"):
            st.session_state["ab_result"] = generate_ab_test(meeting_text)

    if st.session_state.get("ab_result"):
        st.markdown(st.session_state["ab_result"])
        st.download_button("⬇ A/B 아이디어 TXT 다운로드",
            data=st.session_state["ab_result"],
            file_name="able_ab.txt", mime="text/plain")
    else:
        st.info("생성 버튼을 눌러주세요.")

# ── 관련 뉴스 ──
with tab_news:
    st.markdown("#### 관련 트렌드 뉴스")
    st.caption("회의 주제와 관련된 마케팅 / Z세대 / 숏폼 트렌드 뉴스 5건을 AI가 요약합니다.")

    news_kw = st.text_input(
        "검색 키워드 (선택)",
        placeholder="예: Z세대 리브랜딩, 숏폼 바이럴 — 비워두면 회의 내용 기반으로 자동 검색",
        key="sf_news_kw",
    )
    if st.button("뉴스 가져오기", key="btn_news", use_container_width=False):
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
                file_name="able_news.txt", mime="text/plain")
    else:
        st.info("뉴스 가져오기 버튼을 눌러주세요.")
