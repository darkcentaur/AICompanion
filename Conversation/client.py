import pyaudio
import wave
import keyboard
import requests
import base64
import json
import time
import threading
from tqdm import tqdm

# ANSI escape code for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# Pyaudio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 21000
RECORD_SECONDS = 0.05
CHUNK = int(RATE * RECORD_SECONDS)
WAVE_OUTPUT_FILENAME = "voice.wav"

# Function to create a typing effect
def typing_effect(text, color=RESET_COLOR):
    for char in text:
        print(color + char + RESET_COLOR, end='', flush=True)
        time.sleep(0.05)
    print()

# Function to create a loading animation
def loading_animation():
    animation = ['|', '/', '-', '\\']
    idx = 0
    while not loading_complete:
        print(f"\rLoading... {animation[idx]}", end='', flush=True)
        idx = (idx + 1) % len(animation)
        time.sleep(0.1)

# Function to stop the loading animation
def stop_loading_animation():
    global loading_complete
    loading_complete = True
    time.sleep(0.1)  # Ensure final animation frame is visible
    print("\r" + " " * 20 + "\r", end='', flush=True)  # Clear loading animation line

# Pyaudio setup
audio = pyaudio.PyAudio()
input_stream = audio.open(format=FORMAT, channels=CHANNELS, 
                          rate=RATE, input=True, 
                          frames_per_buffer=CHUNK)

output_stream = audio.open(format=FORMAT, channels=CHANNELS, 
                           rate=RATE, output=True)

# Function to record audio
def record_audio():
    frames = []
    typing_effect("Recording... Press 'q' to stop", CYAN)
    while not keyboard.is_pressed('q'):
        data = input_stream.read(CHUNK)
        frames.append(data)
    return frames

# Function to save audio
def save_audio(frames):
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to play audio
def play_audio(audio_binary):
    output_stream.write(audio_binary)

# Function to upload audio and get response
def audio_upload(conversation_history):
    global loading_complete
    loading_complete = False

    with open(WAVE_OUTPUT_FILENAME, 'rb') as file:
        files = {'file': file}
        data = {'conversation_history': json.dumps(conversation_history)}

        # Start loading animation in a separate thread
        loading_thread = threading.Thread(target=loading_animation)
        loading_thread.start()
        
        response = requests.post(url, files=files, data=data)

        # Stop loading animation after response received
        loading_thread.join(timeout=0.1)  # Ensure loading animation stops
        stop_loading_animation()

    if response.status_code == 200:
        data = response.json()
        transcription = data['transcription']
        response_text = data['response']
        audio_base64 = data['audio']
        
        typing_effect(f'Transcription: {transcription}', NEON_GREEN)
        
        audio_binary = base64.b64decode(audio_base64.encode('utf-8'))
        
        # Play audio in a separate thread
        audio_thread = threading.Thread(target=play_audio, args=(audio_binary,))
        audio_thread.start()

        typing_effect(f'Response: {response_text}', PINK)

        audio_thread.join()  # Ensure the audio thread completes before continuing

        typing_effect("Audio played successfully", YELLOW)
        typing_effect("Press SPACE to start recording. Press ESC to quit.", CYAN)

        # Update conversation history
        conversation_history.append({"role": "user", "content": transcription})
        conversation_history.append({"role": "assistant", "content": response_text})

        # Remain the last 8 messages in history
        if len(conversation_history) > 8:
            del conversation_history[:-8]

    else:
        typing_effect("Error:", response.json(), PINK)

# Function to send AI characteristics to the server
def send_characteristics_to_server(characteristics):
    characteristics_url = 'http://127.0.0.1:5000/set-characteristics'
    response = requests.post(characteristics_url, json=characteristics)
    if response.status_code == 200:
        typing_effect("Server received characteristics successfully.", YELLOW)
    else:
        typing_effect("Failed to send characteristics to server.", PINK)

# Prompt user for AI characteristics
def get_characteristics_from_user():
    typing_effect("Please enter the characteristics for your AI companion:", CYAN)
    personality = input("Personality: ")
    voice_tone = input("Voice Tone: ")
    return {
        "personality": personality,
        "voice_tone": voice_tone,
    }



# Main loop
url = 'http://127.0.0.1:5000/upload'

# Get and set AI characteristics
characteristics = get_characteristics_from_user()
send_characteristics_to_server(characteristics)

# Start recording
typing_effect("Press SPACE to start recording. Press ESC to quit.", CYAN)
conversation_history = []

while True:
    if keyboard.is_pressed('esc'):
        break
    if keyboard.is_pressed('space'):
        frames = record_audio()
        save_audio(frames)
        audio_upload(conversation_history)

# Cleanup
input_stream.stop_stream()
input_stream.close()
output_stream.stop_stream()
output_stream.close()
audio.terminate()
