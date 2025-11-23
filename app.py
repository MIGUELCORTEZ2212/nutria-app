import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from nutria_core.chat_engine import ChatEngine
from nutria_core.voice_utils import whisper_to_text, text_to_speech


# =====================================================
# CONFIG BÁSICA
# =====================================================
load_dotenv()

st.set_page_config(
    page_title="NutrIA – Asistente Nutricional Inteligente",
    page_icon="🥑",
    layout="wide",
)

# =====================================================
# ESTILOS (CSS)
# =====================================================
st.markdown(
    """
<style>
html, body, [class*="css"] {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Fondo suave para toda la app */
.main {
    background-color: #f7f9fb;
}

/* Burbujas de chat */
.chat-user {
    background-color: #d1f2eb;
    padding: 10px 14px;
    border-radius: 16px;
    margin: 6px 0;
    margin-left: 20%;
}
.chat-bot {
    background-color: #fdebd0;
    padding: 10px 14px;
    border-radius: 16px;
    margin: 6px 0;
    margin-right: 20%;
}
.chat-role {
    font-size: 0.8rem;
    color: #555;
    margin-bottom: 2px;
}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# INICIALIZAR MOTOR DE CHAT Y ESTADO
# =====================================================
if "dialog" not in st.session_state:
    # dialog = lista de dicts: {"role": "user"/"assistant", "content": "..."}
    st.session_state.dialog = []

# Motor LLM + tools
chat_engine = ChatEngine(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_llm="gpt-4o-mini",
    system_message=open("system_message.txt", "r", encoding="utf-8").read(),
)

# =====================================================
# HEADER
# =====================================================
st.markdown(
    """
<div style="text-align:center; margin-bottom: 1rem;">
  <h1>🥑 NutrIA</h1>
  <h3>Asistente Nutricional Inteligente</h3>
  <p style="color:#555;">
    Te ayudo a entender alimentos, sustituir opciones menos saludables y diseñar planes
    basados en tus datos (edad, peso, estatura, actividad, objetivo, etc.).
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# =====================================================
# LAYOUT PRINCIPAL: IZQ = CHAT/VOZ, DER = AYUDA
# =====================================================
col_main, col_side = st.columns([2.2, 1])

# -----------------------------------------------------
# COLUMNA DERECHA: EXPLICACIÓN Y EJEMPLOS
# -----------------------------------------------------
with col_side:
    st.markdown("### 🧭 ¿Cómo puede ayudarte NutrIA?")
    st.markdown(
        """
- 🔎 **Consulta alimentos**: “¿Qué tan saludable es el pan integral?”
- 🔁 **Sustituye opciones**: “Quiero cambiar cereales azucarados del desayuno.”
- 🧮 **Plan nutricional**: “Soy hombre, 32 años, 72kg, 1.78m, triatlón, objetivo rendimiento.”
- 🧂 **Control de sodio, azúcar, grasas** según tus metas.
        """
    )

    st.markdown("### 💡 Ejemplos de mensajes")
    st.info(
        "- *“Recomiéndame snacks salados con poco sodio.”*\n"
        "- *“Quiero aumentar proteína sin subir mucho las calorías.”*\n"
        "- *“Dame 3 opciones para desayunar antes de entrenar.”*\n"
    )

    st.markdown("### ℹ️ Tips de uso")
    st.markdown(
        """
- Mientras más contexto des (edad, peso, objetivo, alergias), **mejores recomendaciones**.
- Puedes hablar en lenguaje natural, no hace falta usar palabras técnicas.
- Pruéba la pestaña **🎤 Voz** si prefieres hablar en lugar de escribir.
        """
    )

# -----------------------------------------------------
# COLUMNA IZQUIERDA: CHAT + VOZ
# -----------------------------------------------------
with col_main:
    tab_chat, tab_voice, tab_history = st.tabs(["💬 Chat", "🎤 Voz", "📋 Historial"])

    # =================================================
    # TAB 1: CHAT (con st.chat_input → Enter para enviar)
    # =================================================
    with tab_chat:
        st.subheader("💬 Conversa con NutrIA")

        # Mostrar historial con burbujas
        for msg in st.session_state.dialog:
            role = "Usuario" if msg["role"] == "user" else "NutrIA"
            css_class = "chat-user" if msg["role"] == "user" else "chat-bot"
            st.markdown(
                f"<div class='{css_class}'>"
                f"<div class='chat-role'><b>{role}</b></div>"
                f"{msg['content']}</div>",
                unsafe_allow_html=True,
            )

        # Entrada tipo chat (ENTER envía el mensaje)
        user_input = st.chat_input("Escribe tu mensaje...")

        if user_input:
            # 1) Mostrar mensaje del usuario
            st.session_state.dialog.append({"role": "user", "content": user_input})

            # 2) Construir historial en pares (user, assistant) para el motor
            history_pairs = []
            last_user = None
            for m in st.session_state.dialog:
                if m["role"] == "user":
                    last_user = m["content"]
                elif m["role"] == "assistant" and last_user is not None:
                    history_pairs.append((last_user, m["content"]))
                    last_user = None

            # 3) Llamar al motor de NutrIA
            respuesta = chat_engine.chat(user_input, history_pairs)

            # 4) Guardar respuesta
            st.session_state.dialog.append(
                {"role": "assistant", "content": respuesta}
            )

            # 5) Redibujar inmediatamente
            st.experimental_rerun()

        # =================================================
    # TAB 2: VOZ (grabación nativa de Streamlit)
    # =================================================
    with tab_voice:
        st.subheader("🎤 Habla con NutrIA")

        st.markdown("### 🎙️ Grabar audio desde el micrófono")
        audio_input = st.audio_input("Pulsa el botón para grabar tu voz")

        if audio_input is not None:
            st.success("Audio grabado correctamente. Procesando...")

            # Whisper recibe un archivo-like directamente
            text = whisper_to_text(audio_input)
            st.info(f"📝 Transcripción: {text}")

            # Construcción de historial como pares
            history_pairs = []
            last_user = None
            for m in st.session_state.dialog:
                if m["role"] == "user":
                    last_user = m["content"]
                elif m["role"] == "assistant" and last_user is not None:
                    history_pairs.append((last_user, m["content"]))
                    last_user = None

            respuesta = chat_engine.chat(text, history_pairs)
            st.session_state.dialog.append({"role": "user", "content": text})
            st.session_state.dialog.append({"role": "assistant", "content": respuesta})

            st.success(f"🤖 Respuesta: {respuesta}")

            audio_out = text_to_speech(respuesta)
            st.audio(audio_out)

        st.markdown("---")
        st.markdown("### 📁 Subir archivo de audio (MP3/WAV)")
        audio_file = st.file_uploader("Sube un archivo", type=["mp3", "wav"])

        if audio_file is not None:
            if st.button("Enviar archivo"):
                text = whisper_to_text(audio_file)
                st.info(f"📝 Transcripción: {text}")

                # Historial como pares
                history_pairs = []
                last_user = None
                for m in st.session_state.dialog:
                    if m["role"] == "user":
                        last_user = m["content"]
                    elif m["role"] == "assistant" and last_user is not None:
                        history_pairs.append((last_user, m["content"]))
                        last_user = None

                respuesta = chat_engine.chat(text, history_pairs)
                st.session_state.dialog.append({"role": "user", "content": text})
                st.session_state.dialog.append({"role": "assistant", "content": respuesta})

                st.success(f"🤖 Respuesta: {respuesta}")
                audio_out = text_to_speech(respuesta)
                st.audio(audio_out)

    # =================================================
    # TAB 3: HISTORIAL
    # =================================================
    with tab_history:
        st.subheader("📋 Historial de conversación")

        if not st.session_state.dialog:
            st.info("Aún no hay mensajes. Empieza a chatear en la pestaña 💬 Chat.")
        else:
            for msg in st.session_state.dialog:
                icon = "🧑" if msg["role"] == "user" else "🤖"
                who = "Usuario" if msg["role"] == "user" else "NutrIA"
                st.markdown(f"**{icon} {who}:** {msg['content']}")

        if st.button("🗑 Borrar historial"):
            st.session_state.dialog = []
            st.success("Historial eliminado.")

