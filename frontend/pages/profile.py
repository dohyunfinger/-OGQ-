from __future__ import annotations

import streamlit as st

from backend.profile_service import build_profile
from frontend.components import render_progress
from frontend.state import go_to


HEALTH_OPTIONS = ["없음", "고혈압", "당뇨병", "고지혈증", "심혈관 질환", "간 질환", "신장 질환"]
ALLERGY_OPTIONS = ["없음", "갑각류", "생선", "우유", "대두", "땅콩", "견과류"]


def render_profile_page() -> None:
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    render_progress("1/3", 0.33)
    st.markdown("<div class='title-main' style='font-size:2rem;'>더 정확한 정보를 위해<br>개인정보를 입력해주세요</div>", unsafe_allow_html=True)
    st.markdown("<p class='title-sub'>입력하신 정보는 안전하게 보호됩니다.</p>", unsafe_allow_html=True)

    profile = st.session_state.get("profile", {})

    with st.form("profile_form"):
        age = st.selectbox(
            "나이",
            options=list(range(40, 101)),
            index=max(0, min(60, int(profile.get("age", 65)) - 40)),
            help="세 단위로 선택해주세요.",
        )
        gender = st.radio(
            "성별",
            options=["남성", "여성"],
            horizontal=True,
            index=0 if profile.get("gender", "남성") == "남성" else 1,
        )
        health_status = st.multiselect(
            "현재 건강 상태 (선택)",
            options=HEALTH_OPTIONS,
            default=profile.get("health_status", []),
            placeholder="해당되는 질환을 선택하세요",
        )
        allergies = st.multiselect(
            "알레르기 (선택)",
            options=ALLERGY_OPTIONS,
            default=profile.get("allergies", []),
            placeholder="알레르기가 있다면 선택하세요",
        )

        st.caption("🔒 입력하신 정보는 상담 품질 향상에만 사용됩니다.")
        submitted = st.form_submit_button("다음", type="primary", use_container_width=True)

    if submitted:
        st.session_state["profile"] = build_profile(
            age=age,
            gender=gender,
            health_status=health_status,
            allergies=allergies,
        )
        go_to(3)

    if st.button("이전", use_container_width=True):
        go_to(1)

    st.markdown("</div>", unsafe_allow_html=True)
