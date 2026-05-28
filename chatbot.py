import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()

st.set_page_config(
    page_title="주식 AI 어시스턴트",
    page_icon="📈",
    layout="centered",
)

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .stChatMessage { background-color: #161b22; border-radius: 12px; }
    h1 { color: #00ff88 !important; }
    .stTextInput > div > div { background-color: #161b22; }
    .stButton > button {
        background-color: #00ff88;
        color: #0d1117;
        font-weight: bold;
        border: none;
        border-radius: 8px;
    }
    .stButton > button:hover { background-color: #00cc6a; color: #0d1117; }
    .metric-box {
        background: linear-gradient(135deg, #161b22, #1f2937);
        border: 1px solid #00ff8833;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #9ca3af;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 주식 AI 어시스턴트")
st.caption("종목 분석 · 용어 설명 · 시황 해석 — 무엇이든 물어보세요")

st.markdown("""
<div class="metric-box">
💡 <b>이런 걸 물어보세요</b> &nbsp;|&nbsp;
삼성전자 주가 전망 &nbsp;·&nbsp; PER이 뭐야? &nbsp;·&nbsp; 지금 시장 상황 어때? &nbsp;·&nbsp; 분산투자 전략 알려줘
</div>
""", unsafe_allow_html=True)

# Streamlit Cloud secrets 우선, 없으면 .env 사용
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
model = st.secrets.get("OPENAI_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """당신은 전문 주식 및 투자 AI 어시스턴트입니다. 다음 역할을 수행합니다:

1. 종목 분석: 특정 종목의 재무 지표, 사업 모델, 리스크 요인 분석
2. 투자 개념 설명: PER, PBR, EPS, ROE 등 주식 용어를 쉽게 설명
3. 시황 분석: 시장 동향, 섹터별 흐름, 거시경제 영향 해석
4. 투자 전략: 가치투자, 성장주 투자, 분산투자 등 전략 안내

답변 시 유의사항:
- 실제 투자 결정은 본인 판단임을 항상 명시하세요
- 데이터 기반으로 객관적으로 설명하세요
- 초보자도 이해하기 쉽게 설명하되, 전문성을 유지하세요
- 한국 주식 시장(코스피, 코스닥) 중심으로 답변하되 해외 주식도 다루세요"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("종목명, 투자 용어, 시황 등 무엇이든 질문하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            stream=True,
        )
        reply = st.write_stream(response)

    st.session_state.messages.append({"role": "assistant", "content": reply})

if len(st.session_state.messages) > 1:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

st.markdown("""
<div style="text-align:center; color:#4b5563; font-size:0.75rem; margin-top:40px;">
⚠️ 본 서비스는 정보 제공 목적이며, 투자 결과에 대한 책임은 본인에게 있습니다.
</div>
""", unsafe_allow_html=True)
