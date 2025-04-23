import streamlit as st
import openai
from openai import OpenAI
import time

# Config
MODEL_ID = "asst_DvXPhGU51PPMxTgMlAzIdCkr"
CHAT_HISTORY_KEY = "chat_history"

st.set_page_config(page_title="SIEMPLAI",page_icon="♾️", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #f4f6fa !important;
        transition: background-color 0.5s;
    }
    .user-bubble {
        background-color: #1f3b6f;
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 16px;
        margin: 8px 0 8px auto;
        width: fit-content;
        max-width: 80%;
        text-align: left;
        animation: fadeIn 0.5s ease-in;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    .assistant-bubble {
        background-color: #d1e7dd;
        padding: 12px 16px;
        border-radius: 16px;
        margin: 8px auto 8px 0;
        width: fit-content;
        max-width: 80%;
        text-align: left;
        animation: fadeIn 0.5s ease-in;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @media (prefers-color-scheme: dark) {
        .user-bubble { background-color: #4c4c4c; color: #ffffff; }
        .assistant-bubble { background-color: #2a7d4f; color: #ffffff; }
        body { background-color: #121212; color: #ffffff; }
    }
    .main, .block-container {
        background-color: #f4f6fa !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h3 style='font-size:24px;'>🔍 SIEmens Management  - Product Lifecycle Artificial Intelligence</h3>", unsafe_allow_html=True)


# Sidebar para chave e botão de reset
with st.sidebar:
    openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")
    if st.button("🧹 Limpar histórico"):
        st.session_state[CHAT_HISTORY_KEY] = []
        st.rerun()

if openai_api_key:
    client = OpenAI(api_key=openai_api_key)

    if CHAT_HISTORY_KEY not in st.session_state:
        st.session_state[CHAT_HISTORY_KEY] = []

    st.subheader("💬 Chat com o SIEMPLAI")

    chat_placeholder = st.container()
    input_placeholder = st.empty()

    with chat_placeholder:
        for entry in st.session_state[CHAT_HISTORY_KEY]:
            bubble_class = "user-bubble" if entry["role"] == "user" else "assistant-bubble"
            emoji = "👤" if entry["role"] == "user" else "🤖"
            st.markdown(f'<div class="{bubble_class}">{emoji} {entry["content"]}</div>', unsafe_allow_html=True)

    with input_placeholder:
        user_input = st.chat_input("Digite sua pergunta ao SIEMPLAI...")

    if user_input:
        import streamlit.components.v1 as components
        st.session_state[CHAT_HISTORY_KEY].append({"role": "user", "content": user_input})
        components.html("""
        <script>
            window.scrollTo(0, document.body.scrollHeight);
        </script>
        """, height=0)
        with chat_placeholder:
            st.markdown(f'<div class="user-bubble">👤 {user_input}</div>', unsafe_allow_html=True)

        with chat_placeholder:
            with st.spinner("🔎 Buscando resposta..."):
                thread = client.beta.threads.create(extra_headers={"OpenAI-Beta": "assistants=v2"})
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_input,
                    extra_headers={"OpenAI-Beta": "assistants=v2"}
                )

                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=MODEL_ID,
                    extra_headers={"OpenAI-Beta": "assistants=v2"}
                )

                while run.status in ["queued", "in_progress"]:
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id,
                        extra_headers={"OpenAI-Beta": "assistants=v2"}
                    )

                messages = client.beta.threads.messages.list(
                    thread_id=thread.id,
                    extra_headers={"OpenAI-Beta": "assistants=v2"}
                )

                last_assistant_message = next(
                    (msg for msg in reversed(messages.data) if msg.role == "assistant"),
                    None
                )

                if last_assistant_message:
                    import re
                    raw_response = last_assistant_message.content[0].text.value
                    response_text = re.sub(r"【\\d+:\\d+†source】", "", raw_response)
                    st.session_state[CHAT_HISTORY_KEY].append({"role": "assistant", "content": response_text})
                    st.markdown(f'<div class="assistant-bubble">🤖 {response_text}</div>', unsafe_allow_html=True)
else:
    st.warning("Insira sua chave de API para continuar.")
