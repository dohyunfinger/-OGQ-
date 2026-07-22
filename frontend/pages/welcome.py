from __future__ import annotations

import streamlit as st

from frontend.state import go_to


LANGUAGES = [
    ("한국어", "🇰🇷\n한국어"),
    ("中文", "🇨🇳\n中文\n(중국어)"),
    ("日本語", "🇯🇵\n日本語\n(일본어)"),
]


def render_welcome_page() -> None:
    st.markdown("<div class='mobile-card hero-wrap'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center; position:relative; z-index:2; padding-top:16px;">
            <div style="font-size:4rem; line-height:1; margin-bottom:10px;">🍃</div>
            <div class="title-main">궁금한 정보</div>
            <p class="title-sub">건강식품에 대한 궁금증을<br>쉽고 정확하게 알려드려요</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-label'>언어를 선택해주세요</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    selected = st.session_state.get("language", "한국어")

    for col, (value, label) in zip(cols, LANGUAGES):
        with col:
            if st.button(label, use_container_width=True, key=f"lang_{value}"):
                st.session_state["language"] = value
                selected = value
                if value != "한국어":
                    st.toast("현재 서비스 화면과 답변은 한국어 기준으로 제공됩니다.")

    st.caption(f"선택된 언어: {selected}")
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    if st.button("시작하기", type="primary", use_container_width=True):
        go_to(2)

    st.markdown("</div>", unsafe_allow_html=True)
