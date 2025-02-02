import pyaudio
import wave
import keyboard
import requests
from pydub import AudioSegment
from pydub.playback import play
import base64

#Pyaudio setting
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
RECORD_SECONDS = 0.05
CHUNK = int(RATE*RECORD_SECONDS)
WAVE_OUTPUT_FILENAME = "voice.wav"
frames_list = []

#Pyaudio setup
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, 
                    rate=RATE, input=True, 
                    frames_per_buffer=CHUNK)

#Record function
def record_audio(frames):
    data = stream.read(CHUNK)
    frames.append(data)

#Save audio
def save_audio(frames):
    wf = wave.open(WAVE_OUTPUT_FILENAME,'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    #Output a success save
    print("Audio succesfully saved as", WAVE_OUTPUT_FILENAME)

#Setup connnection to server
url = 'http://127.0.0.1:5000/upload'

#upload audio file
def audio_upload():
    with open(WAVE_OUTPUT_FILENAME,'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
    #Check if request was successful
    if response.status_code == 200:
        data = response.json()
        transcription = data['transcription']
        response_text = data['response']
        audio_base64 = data['audio']
            
        # Print transcription and response_text received from server
        print(f'Transcription: {transcription}')
        print(f'Response: {response_text}')
            
        # Decode base64 audio data and play it
        audio_binary = base64.b64decode(audio_base64.encode('utf-8'))

        try:
            # Convert audio samples to AudioSegment
            audio_segment = AudioSegment(
                audio_binary,
                sample_width=4,  # Assuming 32-bit float audio (4 bytes)
                frame_rate=24000,
                channels=1  # Mono audio
        )
            
            # Play the audio
            play(audio_segment)
            print("Audio played successfully.")

        except Exception as e:
            print(f"Error playing audio: {e}")

    else:
        print("Error:", response.json())

#Main body
print("Press SPACE to start record, press q to quit")
while True:
    if keyboard.is_pressed('space'):
        print("Recording... Press 'q' to stop")
        while not keyboard.is_pressed('q'):
            record_audio(frames_list)
        break

#Stop and close the audio stream
stream.stop_stream()
stream.close()
audio.terminate()

#Save and upload the audio
save_audio(frames_list)
audio_upload()