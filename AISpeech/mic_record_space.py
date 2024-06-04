import pyaudio
import wave
import keyboard
import whisper

#Pyaudio Setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
RECORD_SECONDS = 0.05
CHUNK = int(RATE*RECORD_SECONDS)
WAVE_OUTPUT_FILENAME = "output.wav"
frames_list = []
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

#Record function
def record_audio(frames):
    data = stream.read(CHUNK)
    frames.append(data)

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


#Whisper Setup
model = whisper.load_model("small")

#Main Body
print("Hold SPACE to record")
while True:  
    
    if keyboard.is_pressed('space'):
        while keyboard.is_pressed('space'):
            record_audio(frames_list)                                        
    
    if keyboard.is_pressed('q'):
        print("Recording stopped.")
        break

stream.stop_stream()
stream.close()
audio.terminate()

print("Audio saved as", WAVE_OUTPUT_FILENAME)

audio = whisper.load_audio("output.wav")
audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio).to(model.device)

options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

print(result.text)