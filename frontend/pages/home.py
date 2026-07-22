import streamlit as st

st.set_page_config(
    page_title="노인 AI",
    layout="wide"
)

st.title("😊 AI 생활 도우미")

st.write("무엇을 도와드릴까요?")

st.markdown("---")

if st.button("질문하기", use_container_width=True):

    st.switch_page("pages/loading.py")

st.markdown("---")

col1,col2=st.columns(2)

with col1:

    st.button("🌤 오늘 날씨",use_container_width=True)

    st.button("💊 약 먹는 시간",use_container_width=True)

with col2:

    st.button("🏥 병원 찾기",use_container_width=True)

    st.button("☎ 응급 전화",use_container_width=True)