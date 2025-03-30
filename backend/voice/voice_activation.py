import os
import io
import time
from dotenv import load_dotenv  # pip install python-dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import pvporcupine
import pyaudio
import wave
from openai import OpenAI
import numpy as np
from .text_to_speech import text_to_speech

def record_for_duration(audio_stream, porcupine, duration, sample_rate):
    frames = []
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            try:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                frames.append(pcm)
            except IOError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    print("Input overflowed, continuing...")
                    continue
                raise
    except Exception as e:
        print(f"Error during recording: {e}")
        return None
    return b''.join(frames)

def is_affirmative_response(text: str) -> bool:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that determines if a text response is affirmative (yes) or negative (no). Respond with only 'true' or 'false'."},
            {"role": "user", "content": f"Is this response affirmative (yes) or negative (no)? Text: {text}"}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content.strip().lower() == 'true'

def record_until_stop(audio_stream, porcupine, sample_rate):
    print("Recording... Speak now. (Say 'blueberry' to finish recording)")
    frames = []
    try:
        while True:
            try:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                frames.append(pcm)
                pcm_int = np.frombuffer(pcm, dtype=np.int16)
                keyword_index = porcupine.process(pcm_int)
                if keyword_index == 1:
                    print("Stop keyword 'blueberry' detected.")
                    break
            except IOError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    print("Input overflowed, continuing...")
                    continue
                raise
    except Exception as e:
        print(f"Error during recording: {e}")
        return None
    return b''.join(frames)

def transcribe_audio_from_bytes(audio_bytes, sample_rate):
    if audio_bytes is None:
        return ""
    client = OpenAI()
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)     # mono
        wf.setsampwidth(2)     # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    wav_buffer.seek(0)
    wav_buffer.name = "audio.wav"
    text = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=wav_buffer,
        response_format="text"
    )
    return text

def get_voice_command() -> tuple[bool, str, pyaudio.PyAudio, pvporcupine.Porcupine]:
    access_key = os.environ.get("PV_ACCESS_KEY")
    if not access_key:
        raise ValueError("PV_ACCESS_KEY environment variable not set.")
    
    keywords = ["jarvis", "blueberry"]
    porcupine = pvporcupine.create(access_key, keywords=keywords)
    pa = None
    audio_stream = None

    try:
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Listening for the wake word 'Jarvis'...")
        command = ""
        should_execute = False
        while True:
            try:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm_int = np.frombuffer(pcm, dtype=np.int16)
                keyword_index = porcupine.process(pcm_int)
                if keyword_index == 0:
                    print("Wake word 'Jarvis' detected. Starting recording.")
                    audio_data = record_until_stop(audio_stream, porcupine, porcupine.sample_rate)
                    if audio_data is None:
                        print("Failed to record command audio")
                        return False, "", pa, porcupine
                    transcription = transcribe_audio_from_bytes(audio_data, porcupine.sample_rate)
                    print("Voice command transcription:", transcription)
                    command = transcription.strip()
                    
                    # Add confirmation step with task summary
                    confirmation_prompt = f"Please confirm the following task: {command}. Say yes or no."
                    text_to_speech(confirmation_prompt)
                    print("Waiting for confirmation...")
                    confirmation_audio = record_for_duration(audio_stream, porcupine, 4, porcupine.sample_rate)
                    if confirmation_audio is None:
                        print("Failed to record confirmation audio")
                        return False, command, pa, porcupine
                    confirmation_text = transcribe_audio_from_bytes(confirmation_audio, porcupine.sample_rate)
                    print("Confirmation response:", confirmation_text)
                    
                    should_execute = is_affirmative_response(confirmation_text)
                    break
            except IOError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    print("Input overflowed, continuing...")
                    continue
                raise
    except KeyboardInterrupt:
        print("Voice activation interrupted.")
    except Exception as e:
        print(f"Error during voice activation: {e}")
        return False, "", pa, porcupine
    return should_execute, command, pa, porcupine

if __name__ == "__main__":
    should_execute, cmd, pa, porcupine = get_voice_command()
    print(f"Command: {cmd}")
    print(f"Should execute: {should_execute}")
    # Clean up resources
    if pa:
        pa.terminate()
    if porcupine:
        porcupine.delete()