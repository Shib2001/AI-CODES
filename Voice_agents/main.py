import asyncio
import speech_recognition as sr  # Speech recognition ke liye library import karta hai.
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from openai.helpers import LocalAudioPlayer


env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the project .env file.")


client = OpenAI(api_key=api_key)
async_client = AsyncOpenAI(api_key=api_key)


async def speak_response(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=speech,
        instructions="Speak in a clear and friendly tone.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)


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
            model="gpt-4o-mini",
            messages=[
                {"role":"system", "content":SYSTEM_PROMPT},
                {"role":"user", "content": stt},
            ],
            max_tokens=1024,
        )

        response_text = response.choices[0].message.content
        if not response_text:
            raise RuntimeError("OpenAI returned an empty response.")

        print("AI Response:", response_text)
        asyncio.run(speak_response(response_text))


if __name__ == "__main__":  # File ko direct run karne par hi main function chalata hai.
    main()  # Microphone se audio lekar speech recognition start karta hai.