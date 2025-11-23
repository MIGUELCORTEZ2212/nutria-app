import streamlit as st
from dotenv import load_dotenv
import os
from nutria_core.chat_engine import ChatEngine
from nutria_core.voice_utils import whisper_to_text, text_to_speech

# ===============================
# Cargar variables
# ===============================
load_dotenv()

st.set_page_config(
    page_title="NutrIA – Asistente Nutricional Inteligente",
    page_icon="🥑",
    layout="wide"
)

# ===============================
# ESTILOS PERSONALIZADOS (CSS)
# ===============================
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-weight: 700 !important;
}

.chat-bubble-user {
    background-color: #D1F2EB;
    padding: 12px 16px;
    border-radius: 12px;
    max-width: 70%;
    margin-bottom: 10px;
    margin-left: auto;
}

.chat-bubble-bot {
    background-color: #FDEBD0;
    padding: 12px 16px;
    border-radius: 12px;
    max-width: 70%;
    margin-bottom: 10px;
    margin-right: auto;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# Inicializar el motor del chat
# ===============================
chat_engine = ChatEngine(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_llm="gpt-4o-mini",
    system_message=open("system_message.txt", "r", encoding="utf-8").read()
)

# ===============================
# Historial
# ===============================
if "history" not in st.session_state:
    st.session_state.history = []

# ===============================
# Encabezado con estilo
# ===============================
st.markdown("""
<div style='text-align:center; margin-bottom: 20px;'>
    <h1>🥑 NutrIA</h1>
    <h3 style='color: #555;'>Tu Asistente Nutricional Inteligente</h3>
</div>
""", unsafe_allow_html=True)


# ===============================
# TABS PRINCIPALES
# ===============================
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🎤 Voz", "📋 Historial"])


# ============================================================
# TAB 1 — CHAT
# ============================================================
with tab1:
    st.subheader("💬 Conversa con NutrIA")

    user_input = st.text_input("Escribe tu mensaje:")

    if st.button("Enviar"):
        respuesta = chat_engine.chat(user_input, st.session_state.history)
        st.session_state.history.append(("user", user_input))
        st.session_state.history.append(("bot", respuesta))

    st.write("")

    # Mostrar historial como burbujas
    for sender, text in st.session_state.history:
        if sender == "user":
            st.markdown(f"<div class='chat-bubble-user'>{text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-bot'>{text}</div>", unsafe_allow_html=True)


# ============================================================
# TAB 2 — VOZ
# ============================================================
with tab2:
    st.subheader("🎤 Habla con NutrIA")

    audio_file = st.file_uploader("Sube o graba tu audio (MP3/WAV)", type=["mp3", "wav"])

    if audio_file:
        st.info("Transcribiendo audio...")
        text = whisper_to_text(audio_file)

        st.success(f"📝 Transcripción: {text}")

        respuesta = chat_engine.chat(text, st.session_state.history)
        st.session_state.history.append(("user", text))
        st.session_state.history.append(("bot", respuesta))

        st.success(f"🤖 Respuesta: {respuesta}")

        st.info("🔊 Generando audio…")
        audio_out = text_to_speech(respuesta)
        st.audio(audio_out)


# ============================================================
# TAB 3 — HISTORIAL
# ============================================================
with tab3:
    st.subheader("📋 Historial de conversación")

    if not st.session_state.history:
        st.info("Aún no hay mensajes.")
    else:
        for sender, text in st.session_state.history:
            if sender == "user":
                st.markdown(f"**🧑 Usuario:** {text}")
            else:
                st.markdown(f"**🤖 NutrIA:** {text}")

    if st.button("🗑 Borrar historial"):
        st.session_state.history = []
        st.success("Historial eliminado.")
