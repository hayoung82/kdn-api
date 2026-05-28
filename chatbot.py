import os
from dotenv import load_dotenv
import streamlit as st
import streamlit.components.v1 as components
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
    h1 { color: #00ff88 !important; text-align: center; }

    /* 사이드바 배경 */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
    }

    /* 입력 폼 강조 */
    .input-area {
        background: linear-gradient(135deg, #161b22, #1a2332);
        border: 2px solid #00ff88;
        border-radius: 16px;
        padding: 24px 28px;
        margin: 24px 0;
        box-shadow: 0 0 24px #00ff8833;
    }
    .input-label {
        color: #00ff88;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 10px;
        display: block;
    }

    /* text_input 스타일 */
    .stTextInput > div > div > input {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #00ff8866 !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        padding: 12px 16px !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
        opacity: 1 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 8px #00ff8855 !important;
    }


    /* 채팅 메시지 */
    .stChatMessage { background-color: #161b22 !important; border-radius: 12px; }
    .stChatMessage p, .stChatMessage div, .stChatMessage span, .stChatMessage li {
        color: #9ca3af !important;
    }

    .metric-box {
        background: linear-gradient(135deg, #161b22, #1f2937);
        border: 1px solid #00ff8833;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #9ca3af;
    }

    .footer {
        text-align: center;
        color: #374151;
        font-size: 0.72rem;
        margin-top: 40px;
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# API 초기화 (Streamlit Cloud secrets 우선, 없으면 .env)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    model = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")
except Exception:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    st.error("🔑 API 키가 없습니다.")
    st.markdown("""
    **Streamlit Cloud 설정 방법:**
    1. 앱 우측 하단 **Manage app** 클릭
    2. **Settings → Secrets** 탭 선택
    3. 아래 내용 붙여넣기 후 **Save**
    ```toml
    OPENAI_API_KEY = "sk-proj-..."
    OPENAI_MODEL = "gpt-4o-mini"
    ```
    """)
    st.stop()

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """당신은 전문 주식 및 투자 AI 어시스턴트입니다. 다음 역할을 수행합니다:

1. 종목 분석: 특정 종목의 재무 지표, 사업 모델, 리스크 요인 분석
2. 투자 개념 설명: PER, PBR, EPS, ROE 등 주식 용어를 쉽게 설명
3. 시황 분석: 시장 동향, 섹터별 흐름, 거시경제 영향 해석
4. 투자 전략: 가치투자, 성장주 투자, 분산투자 등 전략 안내

답변 시 유의사항:
- 실제 투자 결정은 본인 판단임을 항상 명시하세요
- 데이터 기반으로 객관적으로 설명하세요
- 초보자도 이해하기 쉽게 설명하되 전문성을 유지하세요
- 한국 주식 시장(코스피, 코스닥) 중심으로 답변하되 해외 주식도 다루세요"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""

def on_enter():
    val = st.session_state.get(f"input_{st.session_state.input_key}", "").strip()
    if val:
        st.session_state.pending_input = val

# ── 사이드바: 이전 질문 리스트 ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 이전 질문 목록")
    questions = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    if questions:
        for i, q in enumerate(reversed(questions), 1):
            st.markdown(f"""
            <div style="
                background-color:#161b22;
                border:1px solid #1f2937;
                border-radius:8px;
                padding:8px 12px;
                margin-bottom:6px;
                font-size:0.82rem;
                color:#9ca3af;
                overflow:hidden;
                text-overflow:ellipsis;
                white-space:nowrap;
            ">
            {i}. {q[:40] + '...' if len(q) > 40 else q}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#4b5563; font-size:0.82rem;">아직 질문이 없습니다.</p>', unsafe_allow_html=True)

# ── 헤더 ──────────────────────────────────────────────────────────────────────
st.title("📈 주식 AI 어시스턴트")

# ── 입력 영역 ─────────────────────────────────────────────────────────────────
st.markdown('<div class="input-area"><span class="input-label">💬 주식에 관한 모든 것을 질문하세요</span></div>', unsafe_allow_html=True)

st.text_input(
    label="질문",
    placeholder="예) 삼성전자 지금 사도 될까요?  /  PER이 뭔가요?  /  오늘 시장 분위기 어때요?",
    label_visibility="collapsed",
    key=f"input_{st.session_state.input_key}",
    on_change=on_enter,
)

components.html("""
<script>
    const s = document.createElement('style');
    s.innerHTML = `
        .stButton button {
            background-color: rgba(151,166,195,0.25) !important;
            border: 1px solid rgba(151,166,195,0.5) !important;
            color: #e6edf3 !important;
        }
    `;
    window.parent.document.head.appendChild(s);
</script>
""", height=0)

col_reset, col_spacer, col_btn = st.columns([1, 4, 1])
with col_reset:
    if st.button("초기화", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.pending_input = ""
        st.session_state.input_key += 1
        st.rerun()
with col_btn:
    if st.button("입력", use_container_width=True):
        on_enter()

# Enter 또는 입력 버튼으로 전송된 메시지 처리
if st.session_state.pending_input:
    text = st.session_state.pending_input
    st.session_state.pending_input = ""
    st.session_state.messages.append({"role": "user", "content": text})
    with st.spinner("분석 중..."):
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
        )
        reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.input_key += 1
    st.rerun()

# ── 예시 힌트 (질문 없을 때만 표시) ──────────────────────────────────────────
if len(st.session_state.messages) == 1:
    st.markdown("""
<div class="metric-box">
💡 <b>이런 걸 물어보세요</b> &nbsp;|&nbsp;
삼성전자 주가 전망 &nbsp;·&nbsp; PER이 뭐야? &nbsp;·&nbsp; 지금 시장 상황 어때? &nbsp;·&nbsp; 분산투자 전략 알려줘
</div>
""", unsafe_allow_html=True)

# ── 대화 히스토리 ─────────────────────────────────────────────────────────────
history = [m for m in st.session_state.messages if m["role"] != "system"]
if history:
    st.markdown("---")
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

st.markdown('<div class="footer">⚠️ 본 서비스는 정보 제공 목적이며, 투자 결과에 대한 책임은 본인에게 있습니다.</div>', unsafe_allow_html=True)
