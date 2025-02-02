from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import re
import gc
import torch

# Text generation function
def text_generation(transcript):

    model_id = "TeTLAB/zephyr-7b-beta_assistant_v1_gptq"

    try:
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            trust_remote_code=True,
            revision="main"
        )

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)

        # Create pipeline
        pipe = pipeline(
            model=model,
            tokenizer=tokenizer,
            task="text-generation"
        )

        prompt = transcript

        # Rearrange prompt
        prompt_template = f'''
        </s>
        {prompt}<s/>
        '''

        # Generate response
        response = pipe(
            prompt_template,
            max_new_tokens=80,
            do_sample=True,
            temperature=0.1,
            top_p=0.95
        )
        
        return response[0]["generated_text"].replace(prompt_template,"").replace('\n','').replace('<|assistant|>','').replace('<s/>','').strip()
    
    except Exception as e:
        print(f"Error generating text: {e}")
        generated_text = ""

    finally:
        # Ensure model and pipe are unloaded and memory is freed
        del model
        del tokenizer
        del pipe
        torch.cuda.empty_cache()
        gc.collect()
        print("Model unloaded and GPU memory freed.")

# Post-process generated response
def extract_complete_sentences(content):

    # Using regex to find all sentences ending with ., !, or?
    matches = re.findall(r'[^.!?]*[.!?]',content)

    # Join all matched sentences into a single string
    complete_text = ''.join(matches).strip()

    return complete_text

if __name__ == "__main__":
    prompt = "Why plants grow under sunlight"
    response = text_generation(prompt)
    print(response)