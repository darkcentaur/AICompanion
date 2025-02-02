from transformers import pipeline
from pydub import AudioSegment
from pydub.playback import play

model = None

def t2s_converter(text):
    global model
    # Initialize the pipeline for text-to-speech
    pipe = pipeline("text-to-speech", model="suno/bark-small")
    # Generate audio output from the input text
    output_audio = pipe(text)
    return output_audio

if __name__ == "__main__":
    content = "Green Plant undergoes photosynthesis to grow high and tall"
    audio_data = t2s_converter(content)

    print(audio_data)
    
    # Extract audio samples and sampling rate
    audio_samples = audio_data['audio'].flatten().tobytes()
    sampling_rate = audio_data['sampling_rate']
    print(sampling_rate)
    
    try:
        # Convert audio samples to AudioSegment
        audio_segment = AudioSegment(
            audio_samples,
            sample_width=4,  # Assuming 32-bit float audio (4 bytes)
            frame_rate=sampling_rate,
            channels=1  # Mono audio
    )
        
        # Play the audio
        play(audio_segment)
        print("Audio played successfully.")
        
    except Exception as e:
        print(f"Error playing audio: {e}")
