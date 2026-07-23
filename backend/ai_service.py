from __future__ import annotations

import json
import random
import time
from typing import Any

from google import genai
from google.genai import types


MODEL_NAME = "gemini-3.5-flash"


class AIServiceError(Exception):
    """Gemini API 처리 중 발생하는 오류."""


SYSTEM_PROMPT = """
당신은 시니어 사용자를 위한 식품·건강식품 정보 도우미입니다.

답변 원칙:
1. 반드시 한국어로 답변합니다.
2. 문장을 짧고 쉽게 작성합니다.
3. 사용자의 나이, 성별, 건강 상태, 알레르기를 참고합니다.
4. 식품명과 시장에서 사용하는 지역 명칭을 존중합니다.
5. 확인되지 않은 효능을 사실처럼 단정하지 않습니다.
6. 질병 치료, 약물 대체, 복용 중단을 권하지 않습니다.
7. 개인의 정확한 섭취량을 확정하지 않습니다.
8. 의약품 복용 중이거나 질환이 있으면 전문가 상담을 안내합니다.
9. 식품명이나 제품 정보가 불확실하면 불확실하다고 밝힙니다.
10. 이미지에서 보이지 않는 성분을 추측하지 않습니다.
"""


STRUCTURED_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "question_text": {
            "type": "string",
            "description": "사용자의 질문을 짧게 정리한 문장",
        },
        "supplement_name": {
            "type": "string",
            "description": (
                "질문에 등장한 식품 또는 건강식품 이름. "
                "불분명하면 '확인 필요'"
            ),
        },
        "summary": {
            "type": "string",
            "description": (
                "시니어가 이해하기 쉬운 핵심 답변. "
                "과장 없이 3~5문장"
            ),
        },
        "intake_table": {
            "type": "array",
            "description": (
                "일반적인 참고 정보를 표 형태로 제공. "
                "정확한 근거가 없으면 빈 배열"
            ),
            "items": {
                "type": "object",
                "properties": {
                    "age_group": {
                        "type": "string",
                        "description": "적용 대상 또는 구분",
                    },
                    "amount": {
                        "type": "string",
                        "description": (
                            "제품 표시사항 또는 일반적 참고량. "
                            "확정할 수 없으면 '제품 표시사항 확인'"
                        ),
                    },
                },
                "required": [
                    "age_group",
                    "amount",
                ],
            },
        },
        "best_time": {
            "type": "string",
            "description": (
                "섭취 시점에 관한 일반적인 안내. "
                "근거가 없으면 제품 표시사항을 확인하도록 안내"
            ),
        },
        "cautions": {
            "type": "array",
            "description": "질환이나 상황에 따른 짧은 주의사항",
            "items": {
                "type": "string",
            },
        },
        "allergy_notes": {
            "type": "array",
            "description": "알레르기 관련 확인 사항",
            "items": {
                "type": "string",
            },
        },
        "medical_warning": {
            "type": "string",
            "description": (
                "의료적 판단을 대신하지 않으며 필요 시 "
                "의사 또는 약사와 상담하라는 안내"
            ),
        },
        "tip": {
            "type": "string",
            "description": "보관, 라벨 확인, 섭취 방법 등의 실용적인 팁",
        },
    },
    "required": [
        "question_text",
        "supplement_name",
        "summary",
        "intake_table",
        "best_time",
        "cautions",
        "allergy_notes",
        "medical_warning",
        "tip",
    ],
}


def _is_retryable_error(error: Exception) -> bool:
    """일시적으로 다시 요청할 수 있는 오류인지 확인한다."""

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


def _call_gemini(
    *,
    client: genai.Client,
    contents: list[Any] | str,
    response_schema: dict[str, Any] | None = None,
    max_retries: int = 3,
) -> str:
    """Gemini 호출과 일시적 오류 재시도를 공통 처리한다."""

    for attempt in range(max_retries + 1):
        try:
            config = None

            if response_schema is not None:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.2,
                )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )

            response_text = (
                response.text.strip()
                if response.text
                else ""
            )

            if not response_text:
                raise AIServiceError(
                    "Gemini 응답 내용이 비어 있습니다."
                )

            return response_text

        except AIServiceError:
            raise

        except Exception as error:
            if not _is_retryable_error(error):
                raise AIServiceError(
                    "Gemini API 호출 중 오류가 발생했습니다: "
                    f"{error}"
                ) from error

            if attempt >= max_retries:
                raise AIServiceError(
                    "현재 Gemini 서버 사용량이 많아 "
                    "답변을 생성하지 못했습니다. "
                    "잠시 후 다시 시도해 주세요."
                ) from error

            delay = (
                2 ** (attempt + 1)
                + random.uniform(0.0, 1.0)
            )
            time.sleep(delay)

    raise AIServiceError(
        "Gemini 응답을 생성하지 못했습니다."
    )


def generate_response(
    api_key: str,
    user_input: str,
) -> str:
    """일반 텍스트 질문에 텍스트 답변을 반환한다."""

    cleaned_input = user_input.strip()

    if not cleaned_input:
        raise ValueError(
            "입력 내용이 비어 있습니다."
        )

    if not api_key or not api_key.strip():
        raise AIServiceError(
            "Gemini API 키가 없습니다."
        )

    client = genai.Client(
        api_key=api_key
    )

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"사용자 질문:\n{cleaned_input}"
    )

    return _call_gemini(
        client=client,
        contents=prompt,
    )


def generate_structured_answer(
    *,
    api_key: str,
    user_question: str,
    profile: dict[str, Any] | None,
    question_method: str,
    image_bytes: bytes | None = None,
    image_mime_type: str | None = None,
) -> dict[str, Any]:
    """
    사용자 질문과 프로필을 바탕으로
    답변 화면에서 사용할 구조화된 결과를 반환한다.
    """

    cleaned_question = user_question.strip()

    if not cleaned_question:
        raise ValueError(
            "질문 내용이 비어 있습니다."
        )

    if not api_key or not api_key.strip():
        raise AIServiceError(
            "Gemini API 키가 없습니다."
        )

    safe_profile = profile or {}

    age = safe_profile.get(
        "age",
        "미입력",
    )
    gender = safe_profile.get(
        "gender",
        "미입력",
    )
    health_status = safe_profile.get(
        "health_status",
        [],
    )
    allergies = safe_profile.get(
        "allergies",
        [],
    )

    health_text = (
        ", ".join(health_status)
        if health_status
        else "없음"
    )

    allergy_text = (
        ", ".join(allergies)
        if allergies
        else "없음"
    )

    prompt = f"""
{SYSTEM_PROMPT}

사용자 정보:
- 나이: {age}
- 성별: {gender}
- 건강 상태: {health_text}
- 알레르기: {allergy_text}
- 질문 방법: {question_method}

사용자 질문:
{cleaned_question}

출력 지침:
- 제공된 JSON 스키마에 맞춰 작성합니다.
- 건강 상태와 알레르기는 주의사항 판단에만 참고합니다.
- 개인 맞춤 의료 진단이나 정확한 복용량을 확정하지 않습니다.
- 섭취량이 제품별로 달라지는 경우 반드시 제품 표시사항을 확인하도록 안내합니다.
- 확실한 정보가 없으면 빈 배열 또는 '확인 필요'로 작성합니다.
""".strip()

    contents: list[Any] = [
        prompt
    ]

    if image_bytes is not None:
        if not image_mime_type:
            raise ValueError(
                "이미지 MIME 타입이 없습니다."
            )

        contents.insert(
            0,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=image_mime_type,
            ),
        )

    client = genai.Client(
        api_key=api_key
    )

    response_text = _call_gemini(
        client=client,
        contents=contents,
        response_schema=STRUCTURED_RESPONSE_SCHEMA,
    )

    try:
        result = json.loads(
            response_text
        )

    except json.JSONDecodeError as error:
        raise AIServiceError(
            "Gemini 구조화 응답을 JSON으로 변환하지 못했습니다."
        ) from error

    if not isinstance(result, dict):
        raise AIServiceError(
            "Gemini 구조화 응답 형식이 올바르지 않습니다."
        )

    result["question_text"] = (
        str(
            result.get(
                "question_text",
                cleaned_question,
            )
        ).strip()
        or cleaned_question
    )

    result["supplement_name"] = (
        str(
            result.get(
                "supplement_name",
                "확인 필요",
            )
        ).strip()
        or "확인 필요"
    )

    result["summary"] = str(
        result.get(
            "summary",
            "답변을 생성하지 못했습니다.",
        )
    ).strip()

    result["best_time"] = str(
        result.get(
            "best_time",
            "",
        )
    ).strip()

    result["medical_warning"] = str(
        result.get(
            "medical_warning",
            "",
        )
    ).strip()

    result["tip"] = str(
        result.get(
            "tip",
            "",
        )
    ).strip()

    for list_key in (
        "intake_table",
        "cautions",
        "allergy_notes",
    ):
        if not isinstance(
            result.get(list_key),
            list,
        ):
            result[list_key] = []

    return result