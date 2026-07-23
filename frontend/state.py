from __future__ import annotations

from copy import deepcopy

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

    # Gemini 답변 TTS
    "answer_audio": None,
    "answer_tts_fallback_required": False,

    # 별도 TTS 입력 도구
    "custom_tts_text": "",
    "custom_tts_audio": None,
    "custom_tts_fallback_required": False,
}


def init_state() -> None:
    """Streamlit 세션 상태를 초기화한다."""

    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(value)


def go_to(page: int) -> None:
    """지정한 페이지로 이동한다."""

    st.session_state["page"] = page
    st.rerun()


def clear_answer_state() -> None:
    """새 질문 전에 이전 답변과 음성을 초기화한다."""

    st.session_state["answer_result"] = None
    st.session_state["answer_audio"] = None
    st.session_state[
        "answer_tts_fallback_required"
    ] = False