import os

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
    page_icon="🦦",
    layout="wide",
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error(
        "⚠️ No se encontró la variable de entorno `OPENAI_API_KEY`.\n\n"
        "Configúrala en Streamlit Cloud o en tu entorno local para usar NutrIA."
    )
    st.stop()

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
    # Mensaje de bienvenida inicial
    st.session_state.dialog.append(
        {
            "role": "assistant",
            "content": (
                "👋 Hola, soy **NutrIA**.\n\n"
                "Puedo ayudarte a analizar alimentos, sugerir sustituciones y generar "
                "un plan nutricional basado en tus datos (edad, peso, estatura, actividad y objetivo)."
            ),
        }
    )

# Motor LLM + tools
chat_engine = ChatEngine(
    api_key=OPENAI_API_KEY,
    model_llm="gpt-4o-mini",
    system_message=open("system_message.txt", "r", encoding="utf-8").read(),
)

# =====================================================
# HEADER
# =====================================================
st.markdown(
    """
<div style="text-align:center; margin-bottom: 1rem;">
  <h1> 🦦 NutrIA </h1>
  <h3>Asistente Nutricional Inteligente</h3>
  <p style='color:#999; font-size:0.85rem; margin-top:4px;'>por: Miguel Cortez</p>
  <p style="color:#555;">
    Analiza la composición nutricional de los alimentos, sugiere sustituciones más saludables
    y diseña planes nutricionales personalizados usando IA y datos reales.
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
- 🔎 **Consulta alimentos**  
  Ej: “¿Qué tan saludable es la quinoa?”
- 🔁 **Sustituir opciones**  
  Ej: “Quiero algo mejor que el pan blanco para el desayuno.”
- 🧮 **Plan nutricional**  
  Ej: “Soy hombre, 32 años, 72 kg, 178 cm, triatlón, objetivo rendimiento.”
- 🎯 **Objetivos específicos**  
  Ej: “Quiero bajar mi consumo de azúcar.” / “Quiero subir proteína.”
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
- Mientras más contexto des (edad, peso, objetivo, entrenamientos), **mejores recomendaciones**.
- Puedes hablar en lenguaje natural, no hace falta usar términos técnicos.
- Pruéba la pestaña **🎤 Voz** si prefieres hablar en lugar de escribir.
        """
    )

# -----------------------------------------------------
# COLUMNA IZQUIERDA: CHAT + VOZ
# -----------------------------------------------------
with col_main:
    tab_chat, tab_voice = st.tabs(["💬 Chat", "🎤 Voz"])

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
            # 1) Guardar mensaje del usuario
            st.session_state.dialog.append(
                {"role": "user", "content": user_input}
            )

            # 2) Construir historial como pares (user, assistant)
            history_pairs = []
            last_user = None
            for m in st.session_state.dialog:
                if m["role"] == "user":
                    last_user = m["content"]
                elif m["role"] == "assistant" and last_user is not None:
                    history_pairs.append((last_user, m["content"]))
                    last_user = None

            # 3) Llamar al motor de chat
            respuesta = chat_engine.chat(user_input, history_pairs)

            # 4) Guardar respuesta
            st.session_state.dialog.append(
                {"role": "assistant", "content": respuesta}
            )

            # 5) Redibujar inmediatamente
            st.rerun()
    # =================================================
    # TAB 2: VOZ (grabación nativa de Streamlit)
    # =================================================
    with tab_voice:
        st.subheader("🎤 Habla con NutrIA")

        st.markdown("### 🎙️ Grabar audio desde el micrófono")
        audio_input = st.audio_input("Pulsa el botón para grabar tu voz")

        # Mover la generación de respuesta a una función que se llama cuando hay audio nuevo
        if audio_input is not None and 'audio_processed' not in st.session_state:
            # Añadir un indicador de que el audio ya fue procesado en esta corrida
            # Esto es solo para que el flujo de procesamiento se ejecute una sola vez
            st.session_state.audio_processed = True

            st.success("Audio grabado correctamente. Procesando...")

            # Convertir audio a texto con Whisper
            text = whisper_to_text(audio_input)
            st.session_state.transcription = text # Guardar transcripción en la sesión
            st.info(f"📝 Transcripción: {st.session_state.transcription}")

            # Construcción de historial como pares
            history_pairs = []
            last_user = None
            for m in st.session_state.dialog:
                if m["role"] == "user":
                    last_user = m["content"]
                elif m["role"] == "assistant" and last_user is not None:
                    history_pairs.append((last_user, m["content"]))
                    last_user = None

            # Chat LLM
            respuesta = chat_engine.chat(text, history_pairs)

            # 1) Guardar en el historial (en el orden correcto)
            st.session_state.dialog.append({"role": "user", "content": text})
            st.session_state.dialog.append({"role": "assistant", "content": respuesta})

            # 2) Guardar la respuesta para la generación de audio
            st.session_state.last_response_text = respuesta

            # 3) Forzar el redibujado
            st.rerun()

        # Lógica de visualización y audio después del rerun
        if 'last_response_text' in st.session_state:
            # 4) Mostrar la respuesta en texto
            st.success(f"🤖 Respuesta: {st.session_state.last_response_text}")

            # 5) Convertir respuesta a audio (solo se hace después del rerun)
            audio_out = text_to_speech(st.session_state.last_response_text, voice="alloy")

            if audio_out and os.path.exists(audio_out):
                try:
                    # Intentar leer el archivo MP3
                    with open(audio_out, "rb") as f:
                        audio_bytes = f.read()
                
                    # Reproducir el audio en Streamlit
                    st.audio(audio_bytes, format="audio/mp3")
                
                except Exception as e:
                    # Si la lectura o reproducción falla
                    st.error(f"No pude reproducir el audio: {e}")
            
                finally:
                    # ¡CRUCIAL! Asegurar la eliminación del archivo después de intentar leerlo
                    os.remove(audio_out) 
                
            else:
                # Si text_to_speech devolvió None o el archivo no existe
                st.warning("No pude generar audio de la respuesta...")

            # 6) Limpiar las variables temporales para la siguiente interacción
            del st.session_state.last_response_text
            if 'audio_processed' in st.session_state:
                del st.session_state.audio_processed
            if 'transcription' in st.session_state:
                del st.session_state.transcription