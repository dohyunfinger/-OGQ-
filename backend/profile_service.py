from __future__ import annotations

from typing import Any


class ProfileServiceError(Exception):
    """사용자 프로필 처리 중 발생하는 오류."""


def _clean_string_list(
    values: list[str] | None,
) -> list[str]:
    """빈 문자열과 중복값을 제거한 문자열 목록을 반환한다."""

    if not values:
        return []

    cleaned_values: list[str] = []

    for value in values:
        cleaned_value = str(value).strip()

        if (
            cleaned_value
            and cleaned_value not in cleaned_values
        ):
            cleaned_values.append(cleaned_value)

    # '없음'과 다른 항목이 동시에 선택되면 '없음'을 제거
    if len(cleaned_values) > 1 and "없음" in cleaned_values:
        cleaned_values.remove("없음")

    return cleaned_values


def build_profile(
    *,
    age: int,
    gender: str,
    health_status: list[str] | None,
    allergies: list[str] | None,
) -> dict[str, Any]:
    """프로필 입력값을 검증하고 표준 딕셔너리로 반환한다."""

    try:
        normalized_age = int(age)
    except (TypeError, ValueError) as error:
        raise ProfileServiceError(
            "나이는 숫자로 입력해야 합니다."
        ) from error

    if normalized_age < 40 or normalized_age > 100:
        raise ProfileServiceError(
            "나이는 40세부터 100세 사이로 입력해 주세요."
        )

    normalized_gender = str(gender).strip()

    if normalized_gender not in {"남성", "여성"}:
        raise ProfileServiceError(
            "성별 입력값이 올바르지 않습니다."
        )

    normalized_health_status = _clean_string_list(
        health_status
    )

    normalized_allergies = _clean_string_list(
        allergies
    )

    return {
        "age": normalized_age,
        "gender": normalized_gender,
        "health_status": normalized_health_status,
        "allergies": normalized_allergies,
    }


def profile_summary(
    profile: dict[str, Any] | None,
) -> dict[str, str]:
    """프로필을 화면 출력용 문자열로 정리한다."""

    safe_profile = profile or {}

    age = safe_profile.get("age", 65)
    gender = str(
        safe_profile.get("gender", "미입력")
    ).strip()

    health_status = _clean_string_list(
        safe_profile.get("health_status")
    )

    allergies = _clean_string_list(
        safe_profile.get("allergies")
    )

    health_status_text = (
        ", ".join(health_status)
        if health_status
        else "없음"
    )

    allergy_text = (
        ", ".join(allergies)
        if allergies
        else "없음"
    )

    return {
        "age": f"{age}세",
        "gender": gender or "미입력",
        "health_status": health_status_text,
        "allergy": allergy_text,
    }