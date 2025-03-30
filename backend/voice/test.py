import os
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

def save_audio_to_wav(audio_data, filename, sample_rate):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

def transcribe_audio(filename):
    # Load a more accurate model (e.g., "small" instead of "base")
    client = OpenAI()
    audio_file = open(filename, "rb")

    text = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",  # Use a more accurate model
        file=audio_file, 
        response_format="text"
    )

    # Normalize text for checking
    lower_text = text.lower()
    
    # Remove the start keyword "jarvis" if present
    '''
    if lower_text.startswith("jarvis"):
        text = text[len("jarvis"):].strip(" ,:-")
    
    # Remove the stop keyword "blueberry" if present at the end
    if lower_text.endswith("blueberry"):
        text = text[:-len("blueberry")].strip(" ,:-")'
    '''
    
    return text

def send_to_main(sentence):
    print(f"Sending to main: {sentence}")

def main():
    # Retrieve access key from environment
    access_key = os.environ.get("PV_ACCESS_KEY")
    if not access_key:
        raise ValueError("PV_ACCESS_KEY environment variable not set. Please set it in your .env file one directory up.")

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
    
    print("Listening for the wake word 'Hey'...")
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm_int = np.frombuffer(pcm, dtype=np.int16)
            keyword_index = porcupine.process(pcm_int)
            if keyword_index == 0:
                print("Wake word 'Hey' detected. Starting recording.")
                audio_data = record_until_stop(audio_stream, porcupine, porcupine.sample_rate)
                temp_filename = "temp_audio.wav"
                save_audio_to_wav(audio_data, temp_filename, porcupine.sample_rate)
                transcription = transcribe_audio(temp_filename)
                print("Transcription:", transcription)
                # If the transcription is exactly "Okay, done!", exit the loop
                if transcription.strip().lower() == "okay, done!":
                    print("Exit command received. Terminating...")
                    break
                confirm = input("Is this what you meant? (yes/no): ")
                if confirm.lower() in ["yes", "y"]:
                    send_to_main(transcription)
                else:
                    print("Let's try again.")
                print("\nListening for the wake word 'Hey'...")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == "__main__":
    main()