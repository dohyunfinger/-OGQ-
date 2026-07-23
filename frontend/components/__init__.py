from __future__ import annotations

import html
import json

import streamlit as st
import streamlit.components.v1 as components


def render_progress(
    step_label: str,
    ratio: float,
) -> None:
    """단계 이름과 진행률을 표시한다."""

    safe_label = html.escape(step_label)
    safe_ratio = max(0.0, min(1.0, ratio))

    st.markdown(
        f"<div class='step-title'>{safe_label}</div>",
        unsafe_allow_html=True,
    )
    st.progress(safe_ratio)


def render_speech_button(
    text: str,
    button_label: str = "음성으로 듣기",
    component_id: str = "browser-speech-button",
    rate: float = 0.88,
) -> None:
    """
    브라우저 내장 TTS로 텍스트를 읽는다.

    안내문처럼 Gemini TTS가 필요 없는 짧은 문장에 사용한다.
    """

    cleaned_text = text.strip()

    if not cleaned_text:
        return

    payload = json.dumps(
        cleaned_text,
        ensure_ascii=False,
    )

    safe_label = html.escape(button_label)

    safe_component_id = "".join(
        character
        for character in component_id
        if character.isalnum() or character in ("-", "_")
    )

    components.html(
        f"""
        <div style="margin-top:12px;">
          <button
            id="{safe_component_id}"
            style="
                width:100%;
                background:#0d7a5d;
                color:white;
                border:none;
                border-radius:18px;
                padding:14px 16px;
                font-size:20px;
                font-weight:800;
                cursor:pointer;
            "
          >
            🔊 {safe_label}
          </button>
        </div>

        <script>
          const button = document.getElementById(
              "{safe_component_id}"
          );

          button.addEventListener("click", () => {{
              const synth = window.speechSynthesis;

              if (!synth) {{
                  alert(
                      "이 브라우저는 음성 읽기를 지원하지 않습니다."
                  );
                  return;
              }}

              synth.cancel();

              const utterance =
                  new SpeechSynthesisUtterance({payload});

              utterance.lang = "ko-KR";
              utterance.rate = {rate};
              utterance.pitch = 1.0;
              utterance.volume = 1.0;

              const voices = synth.getVoices();

              const koreanVoice = voices.find(
                  voice => voice.lang.startsWith("ko")
              );

              if (koreanVoice) {{
                  utterance.voice = koreanVoice;
              }}

              synth.speak(utterance);
          }});
        </script>
        """,
        height=75,
    )