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

def text_to_speech(text: str):
    """
    Convierte texto a audio MP3 usando OpenAI gpt-4o-audio.
    Método oficial 2025.
    """
    from openai import OpenAI
    import tempfile

    try:
        client = OpenAI()

        # GENERAR AUDIO
        response = client.audio.speech.with_streaming_response.create(
            model="gpt-4o-audio",
            voice="alloy",
            input=text
        )

        # GUARDAR EN ARCHIVO TEMPORAL
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(tmp.name)

        return tmp.name

    except Exception as e:
        print("ERROR EN TTS:", e)
        return None
