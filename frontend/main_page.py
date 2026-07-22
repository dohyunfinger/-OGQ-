import streamlit as st

from backend.ai_service import AIServiceError, generate_response


def render_main_page() -> None:
    st.title("SilverLens AI 프로젝트")
    st.caption("웹사이트 연결 테스트")

    st.divider()

    user_input = st.text_area(
        "내용을 입력하세요.",
        placeholder="예: 테스트 문장을 입력하세요.",
        height=150,
    )

    if st.button("실행", use_container_width=True):
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            result = generate_response(
                api_key=api_key,
                user_input=user_input,
            )

            st.success("백엔드 연결 성공")
            st.write(result)

        except KeyError:
            st.error(
                ".streamlit/secrets.toml에 "
                "GEMINI_API_KEY가 설정되어 있지 않습니다."
            )

        except FileNotFoundError:
            st.error(
                ".streamlit/secrets.toml 파일을 찾을 수 없습니다."
            )

        except ValueError as error:
            st.warning(str(error))

        except AIServiceError as error:
            st.error(str(error))

        except Exception as error:
            st.error(f"예상하지 못한 오류가 발생했습니다: {error}")