import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import pyaudio
import speech_recognition as sr  # Speech recognition ke liye library import karta hai.
from dotenv import load_dotenv
from openai import OpenAI


env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

api_key = os.getenv("OPEN_ROUTER") or os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPEN_ROUTER is not set in the project .env file. "
        "Add your OpenRouter API key as OPEN_ROUTER=..."
    )


openrouter_base_url = "https://openrouter.ai/api/v1"
client = OpenAI(
    api_key=api_key,
    base_url=openrouter_base_url,
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-OpenRouter-Title": "Voice Agents",
    },
)
llm_model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
tts_model = os.getenv(
    "OPENROUTER_TTS_MODEL",
    "heygen/heygen-voice-1-turbo:free",
)


def speak_response(speech: str):
    if tts_model.startswith("heygen/") and len(speech) > 5000:
        raise ValueError(
            "HeyGen Voice Turbo supports up to 5,000 characters per request."
        )

    payload = {
        "model": tts_model,
        "input": speech,
        "response_format": "pcm",
    }
    voice = os.getenv("OPENROUTER_TTS_VOICE")
    if voice:
        payload["voice"] = voice
    elif tts_model.startswith("heygen/"):
        payload["voice"] = "nadine"

    request = urllib.request.Request(
        f"{openrouter_base_url}/audio/speech",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-OpenRouter-Title": "Voice Agents",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            audio_data = response.read()
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"OpenRouter TTS request failed ({error.code}): {details}"
        ) from error

    player = pyaudio.PyAudio()
    stream = None
    try:
        if not audio_data:
            raise RuntimeError("OpenRouter TTS returned empty audio.")
        if len(audio_data) % 2:
            raise RuntimeError("OpenRouter TTS returned invalid 16-bit PCM audio.")

        stream = player.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            output=True,
        )
        chunk_size = 4096
        for offset in range(0, len(audio_data), chunk_size):
            stream.write(audio_data[offset : offset + chunk_size])
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        player.terminate()


def main():
    r = sr.Recognizer()  # Recognizer object banata hai jo audio ko text mein convert karega.
    with sr.Microphone() as source: # This line is used to ask for the user microphone access
        r.adjust_for_ambient_noise(source) # this will implement the noice cancellation here 
        r.pause_threshold = 2 # Now if user pauses for 2 seconds then we are going to start the process to convert it into text 

        print("Speak something.....")
        audio = r.listen(source) # here we are gonna get the user audio 


        print("Processing Audio .... (STT)")
        stt = r.recognize_google(audio) # and here we are gonna able to process it

        print("You Said:", stt) # and print it on the screen 

        SYSTEM_PROMPT = """
    You are a helpful AI assistant. You are given the transcript of what
    the user has said using voice. Reply clearly and conversationally.
    """

        response = client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role":"system", "content":SYSTEM_PROMPT},
                {"role":"user", "content": stt},
            ],
            max_tokens=1024,
        )

        response_text = response.choices[0].message.content
        if not response_text:
            raise RuntimeError("OpenRouter returned an empty response.")

        print("AI Response:", response_text)
        speak_response(response_text)


if __name__ == "__main__":  # File ko direct run karne par hi main function chalata hai.
    main()  # Microphone se audio lekar speech recognition start karta hai.