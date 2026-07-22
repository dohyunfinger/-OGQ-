from __future__ import annotations

from pathlib import Path

from backend.faster_whisper_service import (
    FasterWhisperError,
    transcribe_with_whisper,
)


class STTServiceError(Exception):
    """통합 음성인식 서비스 오류."""


def load_food_terms(
    file_path: str = "data/food_terms.txt",
) -> list[str]:
    """식품 용어 목록을 읽는다."""

    path = Path(file_path)

    if not path.exists():
        return []

    return [
        line.strip()
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def transcribe_audio(
    audio_bytes: bytes,
) -> str:
    """녹음된 음성을 한국어 텍스트로 변환한다."""

    if not audio_bytes:
        raise ValueError("녹음된 음성이 없습니다.")

    try:
        return transcribe_with_whisper(
            audio_bytes=audio_bytes,
            food_terms=load_food_terms(),
        )

    except (FasterWhisperError, ValueError):
        raise

    except Exception as error:
        raise STTServiceError(
            f"음성인식 처리 중 오류가 발생했습니다: {error}"
        ) from error