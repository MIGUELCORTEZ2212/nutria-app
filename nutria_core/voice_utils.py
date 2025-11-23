import tempfile
import os
from typing import Optional
from openai import OpenAI

client = OpenAI()

# ======================================================
#  WHISPER → TEXTO
# ======================================================

def whisper_to_text(uploaded_audio) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_audio.read())
            tmp_path = tmp.name

        result = client.audio.transcriptions.create(
            file=open(tmp_path, "rb"),
            model="gpt-4o-mini-transcribe"
        )

        os.remove(tmp_path)
        return result.text

    except Exception as e:
        print("ERROR EN WHISPER:", e)
        return "No pude transcribir el audio. Intenta otra vez."


# ======================================================
#  TEXTO → AUDIO (TTS) — versión correcta
# ======================================================

def text_to_speech(text: str, voice: str = "alloy") -> Optional[str]:
    """
    Convierte texto a MP3 con el modelo TTS y devuelve la ruta del archivo.
    """
    try:
        # Generar audio (regresa bytes)
        audio_bytes = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
        )

        # Guardar temporalmente el MP3
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        with open(tmp_file.name, "wb") as f:
            f.write(audio_bytes)

        return tmp_file.name

    except Exception as e:
        print("ERROR GENERANDO AUDIO:", e)
        return None
