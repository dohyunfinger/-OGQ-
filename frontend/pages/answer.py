from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from backend.profile_service import profile_summary
from backend.tts_service import (
    TTSServiceError,
    generate_speech,
)
from frontend.components import render_progress
from frontend.components.backup_browser_tts import (
    render_backup_browser_tts,
)
from frontend.state import go_to


QUESTION_EMOJI = {
    "채팅으로 질문": "💬",
    "사진으로 질문": "📷",
    "음성으로 질문": "🎙️",
}


def _get_api_key() -> str:
    """Streamlit Secrets에서 Gemini API 키를 읽는다."""

    try:
        api_key = str(
            st.secrets["GEMINI_API_KEY"]
        ).strip()

    except KeyError as error:
        raise KeyError(
            ".streamlit/secrets.toml에 "
            "GEMINI_API_KEY를 설정해 주세요."
        ) from error

    except FileNotFoundError as error:
        raise FileNotFoundError(
            ".streamlit/secrets.toml 파일을 찾을 수 없습니다."
        ) from error

    if not api_key:
        raise KeyError(
            "GEMINI_API_KEY 값이 비어 있습니다."
        )

    return api_key


def _build_answer_speech_text(
    result: dict,
    question_text: str,
) -> str:
    """화면 답변에서 음성으로 읽을 핵심 문장만 조합한다."""

    parts = [
        f"질문은 {question_text} 입니다.",
        result.get("summary", ""),
        result.get("best_time", ""),
        result.get("tip", ""),
        result.get("medical_warning", ""),
    ]

    return " ".join(
        part.strip()
        for part in parts
        if isinstance(part, str) and part.strip()
    )


def _render_answer_tts(
    speech_text: str,
) -> None:
    """Gemini 답변용 음성을 생성하고 실패 시 백업 TTS를 표시한다."""

    st.markdown("### 🔊 답변 음성으로 듣기")

    st.caption(
        "답변을 천천히 읽어 드립니다."
    )

    if st.button(
        "Gemini 음성 만들기",
        key="create_answer_tts",
        type="primary",
        use_container_width=True,
    ):
        try:
            api_key = _get_api_key()

            with st.spinner(
                "듣기 편한 음성을 만들고 있어요..."
            ):
                audio_bytes = generate_speech(
                    api_key=api_key,
                    text=speech_text,
                )

            st.session_state[
                "answer_audio"
            ] = audio_bytes

            st.session_state[
                "answer_tts_fallback_required"
            ] = False

            st.success(
                "답변 음성이 준비되었습니다."
            )

        except (
            TTSServiceError,
            ValueError,
            KeyError,
            FileNotFoundError,
        ) as error:
            st.session_state[
                "answer_audio"
            ] = None

            st.session_state[
                "answer_tts_fallback_required"
            ] = True

            st.warning(
                "Gemini 음성을 현재 사용할 수 없습니다. "
                "백업 음성 기능을 이용해 주세요."
            )

            st.caption(str(error))

    answer_audio = st.session_state.get(
        "answer_audio",
    )

    if answer_audio:
        st.audio(
            answer_audio,
            format="audio/wav",
        )

    if st.session_state.get(
        "answer_tts_fallback_required",
        False,
    ):
        # BACKUP TTS
        render_backup_browser_tts(
            text=speech_text,
            button_label="백업 음성으로 답변 듣기",
            component_id="answer-backup-browser-tts",
        )


def _render_custom_tts_tool() -> None:
    """
    답변과 별개로 사용자가 원하는 문장을 읽게 하는 TTS 도구.

    예:
    - 식품 포장지 문구
    - 복용 안내
    - 가족에게 전달할 문장
    """

    st.markdown("---")

    st.markdown(
        """
        <div class="soft-panel">
            <h3 style="margin-top:0;">
                🔉 원하는 문장 따로 읽기
            </h3>
            <p class="muted">
                읽기 어려운 문장을 입력하면
                음성으로 들려드립니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    custom_text = st.text_area(
        "음성으로 들을 문장을 입력하세요.",
        value=st.session_state.get(
            "custom_tts_text",
            "",
        ),
        placeholder=(
            "예: 이 건강식품은 하루 한 번 식후에 드세요."
        ),
        height=130,
        max_chars=1500,
        key="custom_tts_input",
    )

    st.session_state[
        "custom_tts_text"
    ] = custom_text

    left_column, right_column = st.columns(2)

    with left_column:
        if st.button(
            "Gemini 음성 생성",
            key="create_custom_tts",
            use_container_width=True,
            disabled=not custom_text.strip(),
        ):
            try:
                api_key = _get_api_key()

                with st.spinner(
                    "입력한 문장을 음성으로 만들고 있어요..."
                ):
                    custom_audio = generate_speech(
                        api_key=api_key,
                        text=custom_text,
                    )

                st.session_state[
                    "custom_tts_audio"
                ] = custom_audio

                st.session_state[
                    "custom_tts_fallback_required"
                ] = False

                st.success(
                    "입력한 문장의 음성이 준비되었습니다."
                )

            except (
                TTSServiceError,
                ValueError,
                KeyError,
                FileNotFoundError,
            ) as error:
                st.session_state[
                    "custom_tts_audio"
                ] = None

                st.session_state[
                    "custom_tts_fallback_required"
                ] = True

                st.warning(
                    "Gemini 음성 생성에 실패했습니다. "
                    "백업 음성을 사용해 주세요."
                )

                st.caption(str(error))

    with right_column:
        if st.button(
            "입력 내용 지우기",
            key="clear_custom_tts",
            use_container_width=True,
        ):
            st.session_state[
                "custom_tts_text"
            ] = ""

            st.session_state[
                "custom_tts_audio"
            ] = None

            st.session_state[
                "custom_tts_fallback_required"
            ] = False

            st.rerun()

    custom_audio = st.session_state.get(
        "custom_tts_audio",
    )

    if custom_audio:
        st.audio(
            custom_audio,
            format="audio/wav",
        )

    if st.session_state.get(
        "custom_tts_fallback_required",
        False,
    ):
        # BACKUP TTS
        render_backup_browser_tts(
            text=custom_text,
            button_label="백업 음성으로 입력 문장 듣기",
            component_id="custom-backup-browser-tts",
        )


def render_answer_page() -> None:
    result = st.session_state.get(
        "answer_result"
    )

    if not result:
        st.warning(
            "먼저 질문을 입력해 주세요."
        )

        if st.button(
            "질문 페이지로 이동",
            type="primary",
            use_container_width=True,
        ):
            go_to(3)

        return

    profile = st.session_state.get(
        "profile",
        {},
    )

    profile_view = profile_summary(
        profile
    )

    method = st.session_state.get(
        "question_method",
        "채팅으로 질문",
    )

    question_text = (
        result.get("question_text")
        or st.session_state.get(
            "question_text",
            "",
        )
    )

    ask_time = datetime.now().strftime(
        "오늘 %H:%M"
    )

    st.markdown(
        "<div class='mobile-card'>",
        unsafe_allow_html=True,
    )

    render_progress(
        "3/3",
        1.0,
    )

    st.markdown(
        """
        <div
            class='title-main'
            style='font-size:2rem;'
        >
            맞춤 답변
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p class='title-sub'>
            입력하신 정보를 바탕으로 분석한 결과입니다.
        </p>
        """,
        unsafe_allow_html=True,
    )

    thumb = QUESTION_EMOJI.get(
        method,
        "🍀",
    )

    st.markdown(
        f"""
        <div class="question-card">
            <div class="question-thumb">
                {thumb}
            </div>

            <div class="question-body">
                <div class="pill">질문</div>

                <div class="big-question">
                    {question_text}
                </div>

                <div class="muted">
                    질문 시간: {ask_time}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='soft-panel'>",
        unsafe_allow_html=True,
    )

    supplement_name = result.get(
        "supplement_name",
        "건강식품",
    )

    st.markdown(
        f"### 적정 섭취량 ({supplement_name} 기준)"
    )

    st.write(
        result.get(
            "summary",
            "답변이 없습니다.",
        )
    )

    table_rows = result.get(
        "intake_table"
    ) or []

    if table_rows:
        dataframe = pd.DataFrame(
            table_rows
        )

        dataframe = dataframe.rename(
            columns={
                "age_group": "연령대",
                "amount": "권장 섭취량(하루)",
            }
        )

        st.table(dataframe)

    best_time = result.get(
        "best_time",
        "",
    )

    if best_time:
        st.caption(best_time)

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='soft-panel'>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "### 질환이 있을 경우 주의하세요"
    )

    cautions = result.get(
        "cautions"
    ) or []

    if cautions:
        for item in cautions:
            st.markdown(
                f"<span class='chip-box'>{item}</span>",
                unsafe_allow_html=True,
            )
    else:
        st.write(
            "등록된 주의사항이 없습니다."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div
            class='soft-panel'
            style='background:#fffaf0;'
        >
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "### 알레르기 및 상담 안내"
    )

    allergy_notes = result.get(
        "allergy_notes"
    ) or []

    for note in allergy_notes:
        st.write(f"- {note}")

    medical_warning = result.get(
        "medical_warning",
        "",
    )

    if medical_warning:
        st.write(medical_warning)

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div
            class='soft-panel'
            style='background:#fffdf5;'
        >
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### TIP")

    tip = result.get(
        "tip",
        "",
    )

    if tip:
        st.write(tip)

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander(
        "입력한 정보 보기"
    ):
        first_column, second_column = st.columns(
            2
        )

        with first_column:
            st.write(
                f"**나이:** {profile_view['age']}"
            )
            st.write(
                "**건강 상태:** "
                f"{profile_view['health_status']}"
            )

        with second_column:
            st.write(
                f"**성별:** {profile_view['gender']}"
            )
            st.write(
                "**알레르기:** "
                f"{profile_view['allergy']}"
            )

    st.write("도움이 되었나요?")

    first_column, second_column = st.columns(
        2
    )

    with first_column:
        if st.button(
            "👍",
            key="answer_helpful",
            use_container_width=True,
        ):
            st.toast(
                "좋아요를 남겨주셔서 감사합니다!"
            )

    with second_column:
        if st.button(
            "👎",
            key="answer_not_helpful",
            use_container_width=True,
        ):
            st.toast(
                "더 나은 답변을 만들도록 노력하겠습니다."
            )

    speech_text = _build_answer_speech_text(
        result=result,
        question_text=question_text,
    )

    _render_answer_tts(
        speech_text=speech_text,
    )

    # 답변과 별개인 독립 TTS 입력 도구
    _render_custom_tts_tool()

    bottom_left, bottom_right = st.columns(
        2
    )

    with bottom_left:
        if st.button(
            "다시 질문하기",
            key="ask_again",
            use_container_width=True,
        ):
            st.session_state[
                "answer_audio"
            ] = None

            st.session_state[
                "answer_tts_fallback_required"
            ] = False

            go_to(3)

    with bottom_right:
        if st.button(
            "처음으로",
            key="go_home",
            type="primary",
            use_container_width=True,
        ):
            st.session_state[
                "answer_result"
            ] = None

            st.session_state[
                "question_text"
            ] = ""

            st.session_state[
                "recognized_text"
            ] = ""

            st.session_state[
                "normalized_text"
            ] = ""

            st.session_state[
                "answer_audio"
            ] = None

            st.session_state[
                "custom_tts_audio"
            ] = None

            go_to(1)

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )