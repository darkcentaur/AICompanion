from openai import OpenAI

# ANSI escape code for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Text generation function
def gpt_stream(user_input, character, conversation_history):

    try:
        # Initiate the OpenAI client with the API key
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

        messages = [{"role": "system", "content": character}] + conversation_history + [{"role": "user", "content": user_input}]

        # Send the query to the API with streaming enabled
        stream_completion = client.chat.completions.create(
            model="TheBloke/zephyr-7B-beta-GGUF",
            messages=messages,
            stream=True,
        )

        full_response = ''
        line_buffer = ''

        # Iterate over the streamed completion chunks
        for chunk in stream_completion:
            # Extract the delta content from each chunk
            delta_content = chunk.choices[0].delta.content

            # If delta content is not None, process it
            if delta_content is not None:
                # Add the delta content to the line buffer
                line_buffer += delta_content

                # If a newline character is found, print the line in yellow and clear the buffer
                if '\n' in line_buffer:
                    lines = line_buffer.split('\n')
                    for line in lines[:-1]:          # Print all but the last line (which might be incomplete)
                        '''print(NEON_GREEN + line + RESET_COLOR)'''
                        full_response += line + '\n'
                    line_buffer = lines[-1]         # Keep the last line in the buffer
        
        # Print any remaining content in the buffer in yellow
        if line_buffer:
            '''print(NEON_GREEN + line_buffer + RESET_COLOR)'''
            full_response += line_buffer
        
        # Return the assembled full response
        return full_response
    
    except Exception as e:
        print(f"Error generating text: {e}")
        full_response = ""
        return full_response
    
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    return file_content

if __name__ == "__main__":
    conversation_history = []
    character_filename = read_text_file("characteristic.txt")

    prompt = "Why plants grow under sunlight"
    response = gpt_stream(prompt, character_filename, conversation_history)
    print(PINK + response + RESET_COLOR)
    conversation_history.append({"role": "assistant", "content": response})
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    print(conversation_history)