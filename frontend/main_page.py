import streamlit as st
import os
from PIL import Image

# 1. 메인 타이틀 및 소개
st.title("silverLense팀 프로젝트 시작!!!")
st.write("코드가 성공적으로 작동 중입니다.")

st.markdown("---")

# 2. 팀원 B 수집 데이터 영역 (기초 지식 / 센서 정보)
st.header("1. 프로젝트 기초 지식 및 데이터")

# 텍스트 파일 불러오기 예시
text_file_path = os.path.join("data", "textbook_texts", "sensor_info.txt")
if os.path.exists(text_file_path):
    with open(text_file_path, "r", encoding="utf-8") as f:
        sensor_text = f.read()
    st.subheader("교과서 및 기초 지식 내용")
    st.write(sensor_text)
else:
    st.info("수집된 기초 지식 텍스트 파일(data/textbook_texts/sensor_info.txt)이 준비 중입니다.")

# 3. 이미지 및 센서 핀맵 출력 영역
st.header("2. 센서 핀맵 및 전자부품 사진")

col1, col2 = st.columns(2)

with col1:
    st.subheader("센서 핀맵")
    pinmap_path = os.path.join("assets", "pinmaps", "sensor_pinmap.png")
    if os.path.exists(pinmap_path):
        image = Image.open(pinmap_path)
        st.image(image, caption="센서 핀맵 안내", use_column_width=True)
    else:
        st.info("핀맵 이미지 파일이 준비 중입니다.")

with col2:
    st.subheader("테스트용 전자부품 사진")
    component_path = os.path.join("assets", "components", "component_sample.jpg")
    if os.path.exists(component_path):
        image = Image.open(component_path)
        st.image(image, caption="전자부품 이미지", use_column_width=True)
    else:
        st.info("전자부품 사진 파일이 준비 중입니다.")