import os
import io
from dotenv import load_dotenv  # pip install python-dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import pvporcupine
import pyaudio
import wave
from openai import OpenAI
import numpy as np

def record_until_stop(audio_stream, porcupine, sample_rate):
    print("Recording... Speak now. (Say 'Okay, done!' to finish recording)")
    frames = []
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        frames.append(pcm)
        pcm_int = np.frombuffer(pcm, dtype=np.int16)
        keyword_index = porcupine.process(pcm_int)
        # Here, keyword_index==1 is used for the stop phrase.
        if keyword_index == 1:
            print("Stop keyword 'Okay, done!' detected.")
            break
    return b''.join(frames)

def transcribe_audio_from_bytes(audio_bytes, sample_rate):
    client = OpenAI()
    # Build a proper WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)     # mono
        wf.setsampwidth(2)     # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    wav_buffer.seek(0)
    wav_buffer.name = "audio.wav"  # necessary for the OpenAI API to detect format
    text = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",  # or "whisper-1", adjust as needed
        file=wav_buffer,
        response_format="text"
    )
    return text

def get_voice_command() -> str:
    # Get the Picovoice access key from the environment.
    access_key = os.environ.get("PV_ACCESS_KEY")
    if not access_key:
        raise ValueError("PV_ACCESS_KEY environment variable not set.")
    
    # Use two keywords:
    # index 0: wake word ("jarvis")
    # index 1: stop phrase ("blueberry" used as placeholder for "Okay, done!")
    keywords = ["jarvis", "blueberry"]
    porcupine = pvporcupine.create(access_key, keywords=keywords)

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
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm_int = np.frombuffer(pcm, dtype=np.int16)
            keyword_index = porcupine.process(pcm_int)
            # When wake word is detected (index 0), start recording.
            if keyword_index == 0:
                print("Wake word 'Jarvis' detected. Starting recording.")
                audio_data = record_until_stop(audio_stream, porcupine, porcupine.sample_rate)
                transcription = transcribe_audio_from_bytes(audio_data, porcupine.sample_rate)
                print("Voice command transcription:", transcription)
                command = transcription.strip()
                break
    except KeyboardInterrupt:
        print("Voice activation interrupted.")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()
    return command

if __name__ == "__main__":
    cmd = get_voice_command()
    print("Final command:", cmd)