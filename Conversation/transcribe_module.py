from faster_whisper import WhisperModel
import os

# ANSI escape code for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

model_size = "base.en"
model = None

def load_whisper_model():
    global model
    try:
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
    except Exception as e:
        print(f"Failed to load Whisper model: {e}")
        model = None

def transcribe(file_path):
    global model
    if model is None:
        load_whisper_model()  # Load model if not already loaded
    
    try:
        segments, info = model.transcribe(file_path, beam_size=5)
        # Combine segments
        text_content = ' '.join([segment.text for segment in segments])
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        model = None
    except Exception as e:
        print(f"Error transcribing file: {e}")
        text_content = ""
    finally:
        # Unload model to free GPU memory
        model = None
    
    return text_content

if __name__ == "__main__":
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    audio = "sample.wav"
    text = transcribe(audio)
    print(CYAN + text)