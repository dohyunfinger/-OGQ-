from __future__ import annotations

from google import genai


class AIServiceError(Exception):
    """Gemini API 처리 중 발생하는 오류."""


SYSTEM_PROMPT = """
당신은 시니어 사용자를 위한 식품 전문 AI 도우미입니다.

답변 규칙:
1. 반드시 한국어로 답변합니다.
2. 어려운 전문 용어보다 쉬운 표현을 사용합니다.
3. 한 문장을 짧게 작성합니다.
4. 답변은 기본적으로 3~5문장으로 작성합니다.
5. 시장에서 사용하는 식품명과 지역 명칭을 존중합니다.
6. 식품명이 불확실하면 임의로 추측하지 말고 다시 확인합니다.
7. 외국 식재료는 한국에서 통용되는 이름을 함께 설명합니다.
8. 알레르기, 질환, 약 복용과 관련된 내용은 단정하지 않습니다.
"""


def generate_response(
    api_key: str,
    user_input: str,
) -> str:
    """사용자 입력을 Gemini에 보내고 텍스트 응답을 반환한다."""

    cleaned_input = user_input.strip()

    if not cleaned_input:
        raise ValueError("입력 내용이 비어 있습니다.")

    if not api_key or not api_key.strip():
        raise AIServiceError("Gemini API 키가 없습니다.")

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=(
                f"{SYSTEM_PROMPT}\n\n"
                f"사용자 질문:\n{cleaned_input}"
            ),
        )

        if not response.text:
            raise AIServiceError("AI 응답 내용이 비어 있습니다.")

        return response.text.strip()

    except AIServiceError:
        raise

    except Exception as error:
        raise AIServiceError(
            f"Gemini API 호출 중 오류가 발생했습니다: {error}"
        ) from error