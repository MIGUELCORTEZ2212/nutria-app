import streamlit as st
from dotenv import load_dotenv
import os

from nutria_core.chat_engine import ChatEngine
from nutria_core.voice_utils import whisper_to_text, text_to_speech

load_dotenv()

st.set_page_config(page_title="NutrIA", page_icon="🥑", layout="centered")

st.title("🥑 NutrIA – Asistente Nutricional Inteligente")

if "history" not in st.session_state:
    st.session_state.history = []

chat_engine = ChatEngine(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_llm="gpt-4o-mini",
    system_message=open("system_message.txt").read()
)

user_input = st.text_input("Escribe tu mensaje")

if st.button("Enviar"):
    respuesta = chat_engine.chat(user_input, st.session_state.history)
    st.session_state.history.append((user_input, respuesta))
    st.write(respuesta)

audio_file = st.file_uploader("Habla con NutrIA", type=["wav", "mp3"])

if audio_file:
    texto = whisper_to_text(audio_file)
    respuesta = chat_engine.chat(texto, st.session_state.history)
    st.audio(text_to_speech(respuesta))
    st.write(respuesta)
