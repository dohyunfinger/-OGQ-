from __future__ import annotations

import random
import time

from google import genai


class DialectServiceError(Exception):
    """사투리 해석 중 발생하는 오류."""


DIALECT_PROMPT = """
당신은 한국어 지역 방언을 표준어로 정리하는 전문가입니다.

입력 문장은 제주도, 경상도, 전라도, 충청도, 강원도 등의
지역 방언일 수 있습니다.

규칙:
1. 문장의 의미를 바꾸지 않습니다.
2. 식재료명, 음식명, 시장 용어는 가능한 한 그대로 유지합니다.
3. 물텀벙, 가시오이, 백오이, 제피 같은 지역 식품명을
   임의로 다른 단어로 바꾸지 않습니다.
4. 사용자의 질문에 답하지 않습니다.
5. 표준어로 정리된 질문 한 문장만 반환합니다.
6. 확실하지 않은 식품명은 추측하지 않습니다.
7. 의미를 판단할 수 없으면 "확인 필요: 원문"으로 반환합니다.
"""


def _is_retryable_error(error: Exception) -> bool:
    """재시도할 수 있는 일시적 Gemini 오류인지 확인한다."""

    error_text = str(error).upper()

    retryable_signals = (
        "429",
        "500",
        "503",
        "RESOURCE_EXHAUSTED",
        "INTERNAL",
        "UNAVAILABLE",
        "HIGH DEMAND",
        "DEADLINE_EXCEEDED",
    )

    return any(
        signal in error_text
        for signal in retryable_signals
    )


def normalize_dialect(
    api_key: str,
    transcript: str,
    max_retries: int = 3,
) -> str:
    """사투리 또는 시장 표현을 표준어 질문으로 정리한다."""

    cleaned_text = transcript.strip()

    if not cleaned_text:
        raise ValueError("사투리 해석에 사용할 문장이 비어 있습니다.")

    if not api_key or not api_key.strip():
        raise DialectServiceError("Gemini API 키가 없습니다.")

    client = genai.Client(api_key=api_key)

    prompt = (
        f"{DIALECT_PROMPT}\n\n"
        f"변환할 원문:\n{cleaned_text}"
    )

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )

            if not response.text:
                raise DialectServiceError(
                    "사투리 해석 결과가 비어 있습니다."
                )

            normalized_text = response.text.strip()

            if not normalized_text:
                raise DialectServiceError(
                    "사투리 해석 결과가 비어 있습니다."
                )

            return normalized_text

        except DialectServiceError:
            raise

        except Exception as error:
            if not _is_retryable_error(error):
                raise DialectServiceError(
                    "사투리 해석 중 오류가 발생했습니다: "
                    f"{error}"
                ) from error

            if attempt >= max_retries:
                raise DialectServiceError(
                    "현재 Gemini 서버 사용량이 많아 "
                    "사투리를 해석하지 못했습니다. "
                    "잠시 후 다시 시도해 주세요."
                ) from error

            delay = (2 ** (attempt + 1)) + random.uniform(0.0, 1.0)
            time.sleep(delay)

    raise DialectServiceError(
        "사투리 해석 결과를 생성하지 못했습니다."
    )