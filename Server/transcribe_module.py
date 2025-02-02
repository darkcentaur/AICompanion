from faster_whisper import WhisperModel

model_size = "large-v3"
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
        segments, info = model.transcribe(file_path, beam_size=5, language="en")
        # Combine segments
        text_content = ' '.join([segment.text for segment in segments])
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        print(text_content)
        model = None
    except Exception as e:
        print(f"Error transcribing file: {e}")
        text_content = ""
    finally:
        # Unload model to free GPU memory
        model = None
    
    return text_content