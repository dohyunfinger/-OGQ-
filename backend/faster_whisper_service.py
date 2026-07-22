from __future__ import annotations

import tempfile
from pathlib import Path

from faster_whisper import WhisperModel


class FasterWhisperError(Exception):
    """로컬 Whisper 음성인식 중 발생하는 오류."""


_MODEL: WhisperModel | None = None


def get_model() -> WhisperModel:
    """Whisper 모델을 한 번만 불러온다."""
    global _MODEL

    if _MODEL is None:
        _MODEL = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8",
        )

    return _MODEL


def transcribe_with_whisper(
    audio_bytes: bytes,
    food_terms: list[str] | None = None,
) -> str:
    """WAV 음성을 한국어 텍스트로 변환한다."""

    if not audio_bytes:
        raise ValueError("음성 데이터가 비어 있습니다.")

    terms = food_terms or []

    initial_prompt = (
        "한국 전통시장과 식품에 관한 한국어 대화입니다. "
        "지역 방언과 식재료 명칭이 포함될 수 있습니다."
    )

    if terms:
        initial_prompt += (
            " 등장할 수 있는 식품명: "
            + ", ".join(terms)
        )

    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        model = get_model()

        segments, _ = model.transcribe(
            temp_path,
            language="ko",
            beam_size=5,
            initial_prompt=initial_prompt,
            vad_filter=True,
        )

        transcript_parts = [
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ]

        transcript = " ".join(transcript_parts).strip()

        if not transcript:
            raise FasterWhisperError(
                "음성인식 결과가 비어 있습니다."
            )

        return transcript

    except FasterWhisperError:
        raise

    except Exception as error:
        raise FasterWhisperError(
            f"음성인식 중 오류가 발생했습니다: {error}"
        ) from error

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass