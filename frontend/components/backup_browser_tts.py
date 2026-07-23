from __future__ import annotations

from frontend.components import render_speech_button


# ============================================================
# BACKUP TTS COMPONENT
#
# Gemini TTS가 다음 사유로 실패할 때만 사용:
# - 무료 한도 초과
# - 429 요청 제한
# - 503 서버 과부하
# - TTS Preview 모델 오류
#
# Gemini TTS만 사용하게 되면:
# 1. 이 파일 삭제
# 2. answer.py의 render_backup_browser_tts import 삭제
# 3. answer.py의 호출 부분 삭제
# ============================================================


def render_backup_browser_tts(
    text: str,
    button_label: str = "백업 음성으로 듣기",
    component_id: str = "backup-browser-tts",
) -> None:
    """Gemini TTS 실패 시 브라우저 음성합성을 제공한다."""

    render_speech_button(
        text=text,
        button_label=button_label,
        component_id=component_id,
        rate=0.85,
    )