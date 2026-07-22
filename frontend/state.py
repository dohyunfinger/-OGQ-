from __future__ import annotations

import streamlit as st


DEFAULT_STATE = {
    "page": 1,
    "language": "한국어",
    "profile": {
        "age": 65,
        "gender": "남성",
        "health_status": [],
        "allergies": [],
    },
    "question_method": "채팅으로 질문",
    "question_text": "",
    "recognized_text": "",
    "normalized_text": "",
    "uploaded_image": None,
    "uploaded_image_name": "",
    "uploaded_image_mime": "",
    "answer_result": None,
}


def init_state() -> None:
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(page: int) -> None:
    st.session_state["page"] = page
    st.rerun()
