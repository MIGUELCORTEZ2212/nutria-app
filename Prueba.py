from openai import OpenAI

client = OpenAI()

response = client.audio.speech.with_streaming_response.create(
    model="gpt-4o-audio",
    voice="alloy",
    input="Hola Miguel, esta es una prueba de voz de NutrIA."
)

response.stream_to_file("test_audio.mp3")
print("AUDIO GENERADO OK")
