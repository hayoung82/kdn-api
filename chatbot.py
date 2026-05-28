import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="KDN AI 챗봇",
    page_icon="⚡",
    layout="centered",
)

st.title("⚡ KDN AI 챗봇")
st.caption("한전KDN AI 어시스턴트입니다. 무엇이든 질문해보세요.")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "당신은 KDN(한국전력데이터네트웍스)의 친절한 AI 어시스턴트입니다. 사용자의 질문에 명확하고 간결하게 답변해주세요.",
        }
    ]

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=st.session_state.messages,
                stream=True,
            )
            reply = st.write_stream(response)

    st.session_state.messages.append({"role": "assistant", "content": reply})

if len(st.session_state.messages) > 1:
    if st.button("대화 초기화"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
