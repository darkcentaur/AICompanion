from flask import *
import os
from timer_module import print_waiting_time
from text_generation_module import gpt_stream
import threading
from transcribe_module import transcribe
from t2s_module import t2s_converter

# ANSI escape code for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Setup server
server = Flask(__name__)

# Setup folder for uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allow multiple threads to access lib
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        raise
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        raise

# Home
@server.route('/', methods=['GET'])
def home():
    return "This is the home page"


# Personalised AI
characteristics = {}
@server.route('/set-characteristics', methods=['POST'])
def set_characteristics():
    global characteristics
    characteristics = request.json
    return jsonify({"status": "success", "message": "Characteristics updated."})


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
        
        conversation_history = request.form.get('conversation_history')
        if conversation_history:
            conversation_history = json.loads(conversation_history)
        else:
            conversation_history = []

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
            
            # Open file
            character_filename = json.dumps(characteristics)

            # Generate response
            generated_text = gpt_stream(text_content, character_filename, conversation_history)

            # Signal that the response has been generated
            response_received.set()

            # Wait for the response thread to finish
            response_thread.join()

            # Text-to-Speech convert
            audio_base64 = t2s_converter(generated_text)

            return jsonify({
                'message': 'File uploaded successfully',
                'transcription': text_content,
                'response': generated_text,
                'audio': audio_base64}), 200
    except Exception as e:
        print(f"Error processing upload: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Direct run
if __name__ == '__main__':
    server.run(debug=True)
