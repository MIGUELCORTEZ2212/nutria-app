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

def text_to_speech(text: str) -> Optional[str]:
    """
    Convierte texto en audio MP3 usando el modelo oficial de TTS de OpenAI.
    Devuelve la ruta temporal del archivo generado o None si hay error.
    """
    try:
        response = client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="ash",
            input=text
        )

        # Crear archivo temporal
        import tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

        # Guardar audio
        response.stream_to_file(tmp.name)

        return tmp.name

    except Exception as e:
        print("ERROR TTS:", e)
        return None

