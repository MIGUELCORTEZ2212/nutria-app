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
    Acepta archivos tipo UploadedFile (audio_input).
    """
    try:
        # Guardar el audio temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_audio.read())
            tmp_path = tmp.name

        # Transcribir (modelo correcto)
        result = client.audio.transcriptions.create(
            file=open(tmp_path, "rb"),
            model="gpt-4o-mini-transcribe"
        )

        os.remove(tmp_path)
        return result.text

    except Exception as e:
        print("ERROR EN WHISPER:", e)
        return "No pude transcribir el audio. Intenta de nuevo."


# ======================================================
#  TEXTO → TTS (AUDIO en MP3)
# ======================================================

def text_to_speech(text: str, voice: str = "alloy") -> Optional[str]:
    """
    Convierte texto en audio MP3 con streaming.
    Devuelve la ruta al archivo MP3 generado.
    """

    try:
        # Modelo correcto para TTS streaming
        response = client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text
        )

        # Guardar como archivo temporal .mp3
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(tmp_file.name)

        return tmp_file.name

    except Exception as e:
        print("ERROR GENERANDO AUDIO:", e)
        return None
