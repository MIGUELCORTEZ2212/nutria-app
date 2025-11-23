import tempfile
from typing import Optional

from openai import OpenAI

# Cliente global; usa OPENAI_API_KEY del entorno
client = OpenAI()


# ======================================================
#  WHISPER → TEXTO
# ======================================================

def whisper_to_text(file) -> str:
    """
    Convierte audio en texto usando Whisper.

    - `file` puede ser un objeto tipo UploadedFile de Streamlit.
    """
    try:
        transcript = client.audio.transcriptions.create(
            file=file,
            model="whisper-1",
        )
        return transcript.text
    except Exception:
        return "No pude transcribir el audio, intenta de nuevo o habla más claro."


# ======================================================
#  TEXTO → TTS (AUDIO)
# ======================================================

def text_to_speech(text):
    """Convierte texto en audio MP3 usando TTS."""
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="Ash",
        input=text
    )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    with open(tmp.name, "wb") as f:
        f.write(speech.read())

    return tmp.name
