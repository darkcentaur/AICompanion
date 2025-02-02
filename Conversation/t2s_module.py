import os
import torch
import base64  # For encoding audio data
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter

ckpt_base = 'OpenVoice/checkpoints/base_speakers/EN'
ckpt_converter = 'OpenVoice/checkpoints/converter'
device = "cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = 'outputs'

# Initialize base speaker and tone color converter
base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

# Load source spectral embedding
source_se = torch.load(f'{ckpt_base}/en_default_se.pth').to(device)

# Function to generate audio from text and return base64 encoded audio
def t2s_converter(text):
    try:
        # Path for temporary audio file
        src_path = f'{output_dir}/tmp.wav'
        
        # Generate audio from text using base speaker TTS
        base_speaker_tts.tts(text, src_path, speaker='default', language='English', speed=1.0)
        
        # Extract tone color embedding from reference speaker
        reference_speaker = 'resources/example_reference.mp3'
        target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='processed', vad=True)
        
        # Output path for final audio file
        save_path = f'{output_dir}/output_en_default.wav'
        
        # Convert tone color using converter
        encode_message = "@MyShell"
        tone_color_converter.convert(audio_src_path=src_path, src_se=source_se, tgt_se=target_se, output_path=save_path, message=encode_message)
        
        # Read the generated audio file
        with open(save_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Encode audio data to base64
        encoded_audio = base64.b64encode(audio_data).decode('utf-8')
        
        return encoded_audio
    
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    # Example text input
    input_text = "Who is Goh Shu Wen? I don't know her yet but I love her."
    
    # Generate audio and get base64 encoded audio sample
    audio_sample = t2s_converter(input_text)
    
    if audio_sample:
        print("Generated audio successfully.")
        # Here you can return or use `audio_sample` as needed (e.g., send it back to the server)
    else:
        print("Failed to generate audio.")