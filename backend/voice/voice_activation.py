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
        if keyword_index == 1:
            print("Stop keyword 'Okay, done!' detected.")
            break
    return b''.join(frames)

def transcribe_audio_from_bytes(audio_bytes, sample_rate):
    client = OpenAI()
    # Convert raw PCM audio bytes into a proper WAV file in memory.
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)     # mono audio
        wf.setsampwidth(2)     # pyaudio.paInt16 is 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    wav_buffer.seek(0)
    wav_buffer.name = "audio.wav"  # necessary so that OpenAI recognizes the format
    text = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",  # Use your desired model
        # model = "whisper-1",
        file=wav_buffer,
        response_format="text"
    )
    lower_text = text.lower()
    # Optionally, strip the start ("jarvis") and end ("blueberry") keywords:
    # if lower_text.startswith("jarvis"):
    #     text = text[len("jarvis"):].strip(" ,:-")
    # if lower_text.endswith("blueberry"):
    #     text = text[:-len("blueberry")].strip(" ,:-")
    return text

def send_to_main(sentence):
    print(f"Sending to main: {sentence}")

def main():
    # Retrieve access key from environment
    access_key = os.environ.get("PV_ACCESS_KEY")
    if not access_key:
        raise ValueError("PV_ACCESS_KEY environment variable not set. Please set it in your .env file one directory up.")

    # Configure Porcupine with two keywords: one for the start ("jarvis") and one for the end ("blueberry")
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
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm_int = np.frombuffer(pcm, dtype=np.int16)
            keyword_index = porcupine.process(pcm_int)
            # keyword_index 0 corresponds to the wake keyword ("jarvis")
            if keyword_index == 0:
                print("Wake word 'Jarvis' detected. Starting recording.")
                audio_data = record_until_stop(audio_stream, porcupine, porcupine.sample_rate)
                # Transcribe without saving to disk – use in-memory WAV conversion.
                transcription = transcribe_audio_from_bytes(audio_data, porcupine.sample_rate)
                print("Transcription:", transcription)
                # If the transcription is exactly "Okay, done!" (or you can customize the stop phrase), exit the loop.
                if transcription.strip().lower() == "okay, done!":
                    print("Exit command received. Terminating...")
                    break
                confirm = input("Is this what you meant? (yes/no): ")
                if confirm.lower() in ["yes", "y"]:
                    send_to_main(transcription)
                else:
                    print("Let's try again.")
                print("\nListening for the wake word 'Jarvis'...")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == "__main__":
    main()