import sounddevice as sd
from kokoro import KPipeline

def text_to_speech(text: str, voice: str = 'af_heart', sample_rate: int = 24000) -> None:
    """
    Convert text to speech using the Kokoro TTS model and play it aloud.
    """
    # Initialize the Kokoro pipeline.
    pipeline = KPipeline(lang_code='a')
    
    # The pipeline yields a generator producing tuples of (gs, ps, audio).
    for i, (gs, ps, audio) in enumerate(pipeline(text, voice=voice)):
        print(f"Segment {i}: {gs}, {ps}")
        sd.play(audio, sample_rate)
        sd.wait()  # Wait for playback to finish.

if __name__ == '__main__':
    sample_text = "This is a test of Kokoro text to speech."
    text_to_speech(sample_text, voice='af_heart')