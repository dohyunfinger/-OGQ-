from __future__ import annotations

import streamlit as st

from frontend.pages.answer import render_answer_page
from frontend.pages.profile import render_profile_page
from frontend.pages.question import render_question_page
from frontend.pages.welcome import render_welcome_page
from frontend.state import init_state
from frontend.styles import inject_global_styles


PAGES = {
    1: render_welcome_page,
    2: render_profile_page,
    3: render_question_page,
    4: render_answer_page,
}


def run_app() -> None:
    st.set_page_config(
        page_title="SilverLens | 건강식품 도우미",
        page_icon="🍀",
        layout="centered",
    )

    init_state()
    inject_global_styles()

    page = st.session_state.get("page", 1)
    renderer = PAGES.get(page, render_welcome_page)
    renderer()
