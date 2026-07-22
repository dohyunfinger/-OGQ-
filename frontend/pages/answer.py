import streamlit as st

from components.header import show_header
from components.footer import show_footer
from components.big_button import show_big_button


# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="AI 답변",
    layout="centered"
)


# -----------------------------
# Header
# -----------------------------
show_header("AI 답변")


# -----------------------------
# 답변 카드
# -----------------------------
with st.container(border=True):

    st.markdown(
        """
        <div style="
            font-size:28px;
            line-height:2;
            color:#222222;
            padding:20px;
        ">
            오늘은 오후에 비가 올 예정입니다.<br><br>

            외출하실 때<br>

            우산을 챙기세요.<br><br>

            좋은 하루 보내세요.
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# -----------------------------
# 버튼
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    if show_big_button("다시 질문"):
        st.switch_page("pages/home.py")

with col2:
    if show_big_button("처음으로"):
        st.switch_page("pages/home.py")


st.write("")


# -----------------------------
# Footer
# -----------------------------
show_footer()