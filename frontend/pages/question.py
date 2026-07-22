from __future__ import annotations

import streamlit as st

from backend.ai_service import AIServiceError, generate_structured_answer
from backend.dialect_service import DialectServiceError, normalize_dialect
from backend.faster_whisper_service import FasterWhisperError
from backend.stt_service import STTServiceError, transcribe_audio
from frontend.components import render_progress
from frontend.state import go_to


EXAMPLES = [
    "비타민D는 하루에 얼마나 먹어야 하나요?",
    "홍삼을 먹으면 혈압에 영향을 줄까요?",
    "유산균은 공복에 먹어야 하나요?",
]


def _get_api_key() -> str:
    try:
        return str(st.secrets["GEMINI_API_KEY"]).strip()
    except KeyError as error:
        raise KeyError(".streamlit/secrets.toml에 GEMINI_API_KEY를 설정해주세요.") from error


def _submit_question(method: str, question_text: str, image_bytes: bytes | None = None, image_mime: str | None = None) -> None:
    api_key = _get_api_key()
    profile = st.session_state.get("profile", {})

    with st.spinner("맞춤 답변을 만들고 있어요..."):
        result = generate_structured_answer(
            api_key=api_key,
            user_question=question_text,
            profile=profile,
            question_method=method,
            image_bytes=image_bytes,
            image_mime_type=image_mime,
        )

    st.session_state["question_method"] = method
    st.session_state["question_text"] = question_text
    st.session_state["answer_result"] = result
    go_to(4)


def render_question_page() -> None:
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    render_progress("2/3", 0.66)
    st.markdown("<div class='title-main' style='font-size:2rem;'>궁금한 건강식품에 대해<br>질문해보세요</div>", unsafe_allow_html=True)
    st.markdown("<p class='title-sub'>채팅 또는 사진 또는 음성으로 질문할 수 있습니다.</p>", unsafe_allow_html=True)

    tab_chat, tab_photo, tab_voice = st.tabs(["💬 채팅으로 질문", "📷 사진으로 질문", "🎙️ 음성으로 질문"])

    with tab_chat:
        chat_question = st.text_area(
            "궁금한 내용을 입력해주세요.",
            placeholder="예) 오메가3는 언제 먹는 것이 좋나요?\n프로바이오틱스의 부작용이 있나요?",
            max_chars=1000,
            height=180,
        )
        if st.button("채팅 질문 보내기", key="send_chat", type="primary", use_container_width=True):
            if not chat_question.strip():
                st.warning("질문 내용을 입력해주세요.")
            else:
                try:
                    _submit_question("채팅으로 질문", chat_question.strip())
                except (AIServiceError, KeyError, ValueError) as error:
                    st.error(str(error))

    with tab_photo:
        photo_question = st.text_input(
            "보조 질문",
            placeholder="예) 이 제품은 고혈압이 있어도 먹어도 될까요?",
        )
        photo_file = st.file_uploader(
            "건강식품 라벨이나 성분표 사진 업로드",
            type=["jpg", "jpeg", "png", "webp"],
            key="photo_uploader",
        )
        if photo_file:
            st.image(photo_file, caption="업로드한 사진", use_container_width=True)
        if st.button("사진 질문 보내기", key="send_photo", type="primary", use_container_width=True):
            if photo_file is None:
                st.warning("사진을 먼저 업로드해주세요.")
            else:
                question = photo_question.strip() or "업로드한 건강식품 사진을 보고 주요 성분과 섭취 시 주의점을 쉽게 설명해주세요."
                try:
                    _submit_question(
                        "사진으로 질문",
                        question,
                        image_bytes=photo_file.getvalue(),
                        image_mime=photo_file.type or "image/png",
                    )
                except (AIServiceError, KeyError, ValueError) as error:
                    st.error(str(error))

    with tab_voice:
        audio_file = st.audio_input("마이크 버튼을 누르고 질문해 주세요.", sample_rate=16000)
        if audio_file is not None:
            st.audio(audio_file)
        if st.button("음성 질문 보내기", key="send_voice", type="primary", use_container_width=True):
            if audio_file is None:
                st.warning("음성을 먼저 녹음해주세요.")
            else:
                try:
                    with st.spinner("음성을 글로 바꾸고 있어요..."):
                        transcript = transcribe_audio(audio_file.getvalue())
                    st.session_state["recognized_text"] = transcript

                    api_key = _get_api_key()
                    with st.spinner("사투리나 구어체를 정리하고 있어요..."):
                        normalized = normalize_dialect(api_key=api_key, transcript=transcript)
                    st.session_state["normalized_text"] = normalized

                    st.success("음성 질문을 이해했습니다.")
                    st.info(f"음성 인식: {transcript}")
                    st.info(f"표준어 정리: {normalized}")

                    _submit_question("음성으로 질문", normalized)
                except (
                    FasterWhisperError,
                    STTServiceError,
                    DialectServiceError,
                    AIServiceError,
                    KeyError,
                    ValueError,
                ) as error:
                    st.error(str(error))

    st.markdown("<div class='section-label'>예시 질문</div>", unsafe_allow_html=True)
    for example in EXAMPLES:
        if st.button(example, key=f"example_{example}", use_container_width=True):
            try:
                _submit_question("채팅으로 질문", example)
            except (AIServiceError, KeyError, ValueError) as error:
                st.error(str(error))

    if st.button("이전", use_container_width=True):
        go_to(2)

    st.markdown("</div>", unsafe_allow_html=True)
