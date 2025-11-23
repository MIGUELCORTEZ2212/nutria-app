import tempfile
from openai import OpenAI

client = OpenAI()

# ======================================================
#  WHISPER → TEXTO
# ======================================================

def whisper_to_text(file):
    """Convierte audio en texto usando Whisper."""
    transcript = client.audio.transcriptions.create(
        file=file,
        model="whisper-1"
    )
    return transcript.text


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
