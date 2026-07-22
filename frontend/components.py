from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components


def render_progress(step_label: str, ratio: float) -> None:
    st.markdown(f"<div class='step-title'>{step_label}</div>", unsafe_allow_html=True)
    st.progress(ratio)


def render_speech_button(text: str) -> None:
    payload = json.dumps(text, ensure_ascii=False)
    components.html(
        f"""
        <div style="margin-top:12px;">
          <button onclick='speakAnswer()' style="width:100%; background:#0d7a5d; color:white; border:none; border-radius:18px; padding:14px 16px; font-size:20px; font-weight:800; cursor:pointer;">
            🔊 음성으로 듣기
          </button>
        </div>
        <script>
        function speakAnswer() {{
            const text = {payload};
            const synth = window.speechSynthesis;
            if (!synth) {{
                alert('이 브라우저는 음성 읽기를 지원하지 않습니다.');
                return;
            }}
            synth.cancel();
            const utter = new SpeechSynthesisUtterance(text);
            utter.lang = 'ko-KR';
            utter.rate = 0.95;
            synth.speak(utter);
        }}
        </script>
        """,
        height=70,
    )
