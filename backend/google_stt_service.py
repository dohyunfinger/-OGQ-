from __future__ import annotations

from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech


class GoogleSttError(Exception):
    """Google Chirp 3 처리 중 발생하는 오류."""


def transcribe_with_google(
    project_id: str,
    audio_bytes: bytes,
    region: str = "us",
) -> str:
    """WAV 음성을 Google Chirp 3로 한국어 전사한다."""

    if not project_id or not project_id.strip():
        raise GoogleSttError(
            "Google Cloud 프로젝트 ID가 없습니다."
        )

    if not audio_bytes:
        raise ValueError("음성 데이터가 비어 있습니다.")

    try:
        client = SpeechClient(
            client_options=ClientOptions(
                api_endpoint=f"{region}-speech.googleapis.com"
            )
        )

        recognition_config = cloud_speech.RecognitionConfig(
            auto_decoding_config=(
                cloud_speech.AutoDetectDecodingConfig()
            ),
            language_codes=["ko-KR"],
            model="chirp_3",
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True,
            ),
        )

        request = cloud_speech.RecognizeRequest(
            recognizer=(
                f"projects/{project_id}/locations/"
                f"{region}/recognizers/_"
            ),
            config=recognition_config,
            content=audio_bytes,
        )

        response = client.recognize(request=request)

        transcript_parts: list[str] = []

        for result in response.results:
            if not result.alternatives:
                continue

            text = result.alternatives[0].transcript.strip()

            if text:
                transcript_parts.append(text)

        transcript = " ".join(transcript_parts).strip()

        if not transcript:
            raise GoogleSttError(
                "Google Chirp 3 음성인식 결과가 비어 있습니다."
            )

        return transcript

    except GoogleSttError:
        raise

    except Exception as error:
        raise GoogleSttError(
            f"Google Chirp 3 처리 중 오류가 발생했습니다: {error}"
        ) from error