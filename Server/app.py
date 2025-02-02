from flask import *
import os
from faster_whisper import WhisperModel
from timer_module import print_waiting_time
from text_generation_module import text_generation, extract_complete_sentences
import threading
from transcribe_module import load_whisper_model, transcribe
from t2s_module import t2s_converter
import base64

# Setup server
server = Flask(__name__)

# Setup folder for uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allow multiple threads to access lib
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Home
@server.route('/', methods=['GET'])
def home():
    return "This is the home page"

# Saving uploaded file
@server.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check file uploaded?
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        # Check file name
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = file.filename
            file_path = os.path.join(server.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Transcribe the audio file
            text_content = transcribe(file_path)

            if not text_content:
                return jsonify({'error': 'Failed to transcribe file'}), 500

            # Event to signal completion of text generation
            response_received = threading.Event()

            # Start waiting time thread
            response_thread = threading.Thread(target=print_waiting_time, args=(response_received,))
            response_thread.start()

            # Generate response
            generated_text = text_generation(text_content)

            # Extract full sentences
            final_text = extract_complete_sentences(generated_text)

            # Signal that the response has been generated
            response_received.set()

            # Wait for the response thread to finish
            response_thread.join()

            # Text-to-Speech convert
            audio_data = t2s_converter(final_text)
            
            # Encode audio data to Base64
            audio_base64 = base64.b64encode(audio_data['audio'].flatten().tobytes()).decode('utf-8')

            return jsonify({
                'message': 'File uploaded successfully',
                'transcription': text_content,
                'response': final_text,
                'audio': audio_base64}), 200
    except Exception as e:
        print(f"Error processing upload: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Direct run
if __name__ == '__main__':
    server.run(debug=True)
