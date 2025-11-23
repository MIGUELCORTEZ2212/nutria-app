import tempfile
import os
from typing import Optional
from openai import OpenAI

client = OpenAI()

# ======================================================
#  WHISPER → TEXTO
# ======================================================

def whisper_to_text(uploaded_audio) -> str:
    """
    Convierte audio grabado desde Streamlit en texto usando Whisper.
    """
    try:
        # Guardar audio temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_audio.read())
            tmp_path = tmp.name

        # Modelo correcto de whisper
        result = client.audio.transcriptions.create(
            file=open(tmp_path, "rb"),
            model="gpt-4o-mini-transcribe"  # <-- Modelo correcto
        )

        os.remove(tmp_path)
        return result.text

    except Exception as e:
        print("ERROR EN WHISPER:", e)
        return "No pude transcribir el audio. Intenta otra vez."


# ======================================================
#  TEXTO → AUDIO MP3 (TTS)
# ======================================================

def text_to_speech(text: str, voice: str = "alloy") -> Optional[str]:
    """
    Convierte texto a un archivo MP3 y devuelve la ruta temporal.
    """
    try:
        # Modelo correcto de TTS con streaming
        response = client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",  # <-- ESTE ES EL BUENO
            voice=voice,
            input=text,
        )

        # Guardar como archivo .mp3
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(tmp_file.name)

        return tmp_file.name

    except Exception as e:
        print("ERROR GENERANDO AUDIO:", e)
        return None
