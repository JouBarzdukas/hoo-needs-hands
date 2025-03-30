import sounddevice as sd
import random
from kokoro import KPipeline

def text_to_speech(text: str, voice: str = 'af_heart', sample_rate: int = 24000) -> None:
    """
    Convert text to speech using the Kokoro TTS model and play it aloud.
    """
    # Initialize the Kokoro pipeline.
    pipeline = KPipeline(lang_code='a')
    
    # The pipeline yields a generator producing tuples of (gs, ps, audio).
    for i, (gs, ps, audio) in enumerate(pipeline(text, voice=voice)):
        print(f"Segment {i}: {gs}")
        sd.play(audio, sample_rate)
        sd.wait()  # Wait for playback to finish.
        
def random_auto_response() -> None:
    """
    Generate a random auto-response based on the input text. Simple confirmation for the user, 
    no need to get crazy with API calls
    and LLMs.
    """
    responses = [
        "Got it! I'll start now!",
        "Perfect, I'll take care of that.",
        "Let me get started on that.",
        "Sure thing!",
        "Okay Let's do that!",
        "On it!",
        "Absolutely, I'll try my best!",
    ]
    # Randomly select a response from the list.
    pipeline = KPipeline(lang_code='a')
    response = random.choice(responses)
    # Use the Kokoro TTS model to convert the response to speech.
    for i, (gs, ps, audio) in enumerate(pipeline(response, voice='af_heart')):
        print(f"Auto-response {i}: {gs}")
        sd.play(audio, 24000)
        sd.wait()  # Wait for playback to finish.
if __name__ == '__main__':
    sample_text = "This is a test of Kokoro text to speech."
    text_to_speech(sample_text, voice='af_heart')