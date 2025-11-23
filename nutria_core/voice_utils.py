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

def text_to_speech(text: str, voice: str = "alloy") -> str | None:
    """
    Convierte texto en un archivo MP3 usando el modelo oficial
    de Text-to-Speech de OpenAI.
    Retorna la ruta del archivo generado o None si falla.
    """
    try:
        # Crear respuesta de audio con el modelo correcto
        response = client.audio.speech.with_streaming_response.create(
            model="gpt-4o-audio",   # ← MODELO CORRECTO
            voice=voice,  # alloy / nova / shimmer / verse
            input=text
        )

        # Crear archivo temporal .mp3
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

        # Guardar audio en el archivo
        response.stream_to_file(tmp_file.name)

        return tmp_file.name

    except Exception as e:
        print("ERROR GENERANDO AUDIO:", e)
        return None
