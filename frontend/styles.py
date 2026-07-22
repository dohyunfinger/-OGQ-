from __future__ import annotations

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f4fbf8 0%, #ffffff 18%, #eef8f5 100%);
        }
        .block-container {
            max-width: 540px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        .mobile-card {
            background: rgba(255,255,255,0.95);
            border-radius: 28px;
            padding: 24px 22px;
            box-shadow: 0 10px 30px rgba(18, 93, 70, 0.08);
            border: 1px solid rgba(13, 110, 83, 0.06);
        }
        .hero-wrap {
            position: relative;
            overflow: hidden;
        }
        .hero-wrap::before {
            content: "";
            position: absolute;
            right: -40px;
            top: -30px;
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: rgba(16, 131, 100, 0.08);
        }
        .hero-wrap::after {
            content: "";
            position: absolute;
            left: -70px;
            bottom: -90px;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: rgba(16, 131, 100, 0.06);
        }
        .title-main {
            color: #0d6b55;
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 0.4rem;
        }
        .title-sub {
            color: #6f7774;
            font-size: 1.05rem;
            line-height: 1.6;
            margin-bottom: 0;
        }
        .section-label {
            color: #1f2523;
            font-size: 1.05rem;
            font-weight: 800;
            margin: 1.4rem 0 0.9rem;
        }
        .chip-box {
            display: inline-block;
            padding: 0.36rem 0.7rem;
            border-radius: 999px;
            background: #fff4f4;
            color: #cf4a57;
            font-size: 0.9rem;
            margin: 0.2rem 0.28rem 0.2rem 0;
            border: 1px solid #ffd9dd;
        }
        .soft-panel {
            background: #ffffff;
            border: 1px solid #e8efeb;
            border-radius: 18px;
            padding: 16px;
            margin-top: 12px;
        }
        .question-card {
            display: flex;
            gap: 14px;
            align-items: stretch;
            background: #ffffff;
            border: 1px solid #e6eeea;
            border-radius: 20px;
            overflow: hidden;
            margin-top: 0.8rem;
        }
        .question-thumb {
            width: 140px;
            min-height: 140px;
            background: linear-gradient(180deg, #f5f7f6, #edf3f1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
        }
        .question-body {
            flex: 1;
            padding: 14px 14px 14px 0;
        }
        .pill {
            display: inline-block;
            background: #0d7a5d;
            color: white;
            border-radius: 999px;
            padding: 0.2rem 0.7rem;
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }
        .big-question {
            font-size: 1.9rem;
            font-weight: 800;
            line-height: 1.3;
            color: #1e2422;
            margin-bottom: 0.4rem;
        }
        .muted {
            color: #737c78;
            font-size: 0.94rem;
        }
        .bottom-actions {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-top: 1rem;
        }
        .voice-button-note {
            background: #0d7a5d;
            color: white;
            border-radius: 18px;
            padding: 0.85rem 1rem;
            text-align: center;
            font-weight: 800;
            width: 100%;
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(90deg, #0e6f58 0%, #0f8666 100%);
            border: none;
            border-radius: 999px;
            min-height: 3.2rem;
            font-weight: 800;
            font-size: 1.06rem;
        }
        div[data-testid="stButton"] > button {
            border-radius: 16px;
        }
        .lang-button button,
        .select-card button {
            min-height: 120px;
            white-space: pre-line;
            font-weight: 700;
        }
        .step-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #41675c;
            background: #eef7f3;
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            margin-bottom: 0.8rem;
        }
        table {
            border-collapse: collapse !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
