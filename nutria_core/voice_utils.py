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
    Convierte audio grabado desde Streamlit en texto usando GPT-4o-mini-Transcribe.
    """
    try:
        # Guardar el audio temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(uploaded_audio.read())
            tmp_path = tmp.name

        # Modelo de transcripción correcto
        result = client.audio.transcriptions.create(
            file=open(tmp_path, "rb"),
            model="gpt-4o-mini-transcribe",
        )

        os.remove(tmp_path)
        return result.text

    except Exception as e:
        # Esto se verá en la consola de Streamlit
        print("ERROR EN WHISPER:", repr(e))
        return "No pude transcribir el audio. Intenta otra vez."


# ======================================================
#  TEXTO → AUDIO MP3 (TTS)
# ======================================================

def text_to_speech(text: str, voice: str = "alloy") -> Optional[str]:
    """
    Convierte texto a un archivo MP3 y devuelve la ruta temporal.
    Usa el modelo gpt-4o-mini-tts y la API correcta.
    """
    try:
        # Llamada correcta al endpoint de TTS
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,       # alloy, nova, verse, shimmer...
            input=text,
        )

        # Guardar salida en un archivo temporal .mp3
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(tmp_file.name)

        return tmp_file.name

    except Exception as e:
        # MUY IMPORTANTE: mostrar el error real en consola
        print("ERROR GENERANDO AUDIO:", repr(e))
        return None
