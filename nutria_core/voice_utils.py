import tempfile
import os
from typing import Optional
from openai import OpenAI

client = OpenAI()

# ======================================================
#  WHISPER → TEXTO (Streamlit audio compatible)
# ======================================================

def whisper_to_text(uploaded_audio) -> str:
    """
    Convierte audio grabado desde Streamlit en texto usando Whisper.
    Acepta archivos tipo UploadedFile (audio_input).
    """

    try:
        # Guardar audio temporalmente como archivo real
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_audio.read())
            tmp_path = tmp.name

        # Transcribir
        result = client.audio.transcriptions.create(
            file=open(tmp_path, "rb"),
            model="gpt-4o-transcribe"
        )

        # Eliminar temporal
        os.remove(tmp_path)

        return result.text

    except Exception as e:
        print("ERROR EN WHISPER:", e)
        return "No pude transcribir el audio, intenta de nuevo o habla más claro."


# ======================================================
#  TEXTO → TTS (AUDIO en MP3)
# ======================================================

def text_to_speech(text: str, voice: str = "alloy") -> Optional[str]:
    """
    Convierte texto en audio MP3 con streaming.
    Devuelve la ruta al archivo MP3 generado.
    """

    try:
        response = client.audio.speech.with_streaming_response.create(
            model="gpt-4o-audio",
            voice=voice,   # Voces válidas: alloy, nova, verse, shimmer
            input=text
        )

        # Guardar como archivo temporal .mp3
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(tmp_file.name)

        return tmp_file.name

    except Exception as e:
        print("ERROR GENERANDO AUDIO:", e)
        return None
