from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from backend.profile_service import profile_summary
from frontend.components import render_progress, render_speech_button
from frontend.state import go_to


QUESTION_EMOJI = {
    "채팅으로 질문": "💬",
    "사진으로 질문": "📷",
    "음성으로 질문": "🎙️",
}


def render_answer_page() -> None:
    result = st.session_state.get("answer_result")
    if not result:
        st.warning("먼저 질문을 입력해주세요.")
        if st.button("질문 페이지로 이동", type="primary", use_container_width=True):
            go_to(3)
        return

    profile = st.session_state.get("profile", {})
    profile_view = profile_summary(profile)
    method = st.session_state.get("question_method", "채팅으로 질문")
    question_text = result.get("question_text") or st.session_state.get("question_text", "")
    ask_time = datetime.now().strftime("오늘 %H:%M")

    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    render_progress("3/3", 1.0)
    st.markdown("<div class='title-main' style='font-size:2rem;'>맞춤 답변</div>", unsafe_allow_html=True)
    st.markdown("<p class='title-sub'>입력하신 정보를 바탕으로 분석한 결과입니다.</p>", unsafe_allow_html=True)

    thumb = QUESTION_EMOJI.get(method, "🍀")
    st.markdown(
        f"""
        <div class="question-card">
            <div class="question-thumb">{thumb}</div>
            <div class="question-body">
                <div class="pill">질문</div>
                <div class="big-question">{question_text}</div>
                <div class="muted">질문 시간: {ask_time}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='soft-panel'>", unsafe_allow_html=True)
    st.markdown(f"### 적정 섭취량 ({result.get('supplement_name', '건강식품')} 기준)")
    st.write(result.get("summary", "답변이 없습니다."))

    table_rows = result.get("intake_table") or []
    if table_rows:
        df = pd.DataFrame(table_rows)
        rename_map = {"age_group": "연령대", "amount": "권장 섭취량(하루)"}
        df = df.rename(columns=rename_map)
        st.table(df)

    st.caption(result.get("best_time", ""))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='soft-panel'>", unsafe_allow_html=True)
    st.markdown("### 질환이 있을 경우 주의하세요")
    cautions = result.get("cautions") or []
    if cautions:
        for item in cautions:
            st.markdown(f"<span class='chip-box'>{item}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='soft-panel' style='background:#fffaf0;'>", unsafe_allow_html=True)
    st.markdown("### 알레르기 및 상담 안내")
    allergy_notes = result.get("allergy_notes") or []
    for note in allergy_notes:
        st.write(f"- {note}")
    st.write(result.get("medical_warning", ""))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='soft-panel' style='background:#fffdf5;'>", unsafe_allow_html=True)
    st.markdown("### TIP")
    st.write(result.get("tip", ""))
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("입력한 정보 보기"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**나이:** {profile_view['age']}")
            st.write(f"**건강 상태:** {profile_view['health_status']}")
        with col2:
            st.write(f"**성별:** {profile_view['gender']}")
            st.write(f"**알레르기:** {profile_view['allergy']}")

    st.write("도움이 되었나요?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍", use_container_width=True):
            st.toast("좋아요를 남겨주셔서 감사합니다!")
    with col2:
        if st.button("👎", use_container_width=True):
            st.toast("더 나은 답변을 만들도록 노력하겠습니다.")

    speech_text = " ".join(
        [
            question_text,
            result.get("summary", ""),
            result.get("best_time", ""),
            result.get("tip", ""),
            result.get("medical_warning", ""),
        ]
    )
    render_speech_button(speech_text)

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        if st.button("다시 질문하기", use_container_width=True):
            go_to(3)
    with bottom_right:
        if st.button("처음으로", type="primary", use_container_width=True):
            st.session_state["answer_result"] = None
            st.session_state["question_text"] = ""
            st.session_state["recognized_text"] = ""
            st.session_state["normalized_text"] = ""
            go_to(1)

    st.markdown("</div>", unsafe_allow_html=True)
