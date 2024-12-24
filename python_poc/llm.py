import os
import torch
from transformers import LlamaTokenizer, MistralForCausalLM
import torch
import gc

# Supply vault directory here
vault_dir = "/mnt/d/Documents/ObsidianDev"

torch.cuda.empty_cache()

# Lists md files in root dir
def list_files_recursively(root_dir):
    file_list = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # removes .obsidian directory from search path
        dirnames[:] = [d for d in dirnames if d != '.obsidian']
        for file in filenames:
            file_list.append(os.path.join(dirpath, file))
    return [f for f in file_list if f.endswith('.md')]

# splits strings into 1000 char chunks
def chunk_string(inp, chunk_size=2000):
    return [inp[i:i+chunk_size] for i in range(0, len(inp), chunk_size)]

def load_model():
    # Load tokenizer and model
    tokenizer = LlamaTokenizer.from_pretrained('NousResearch/Nous-Hermes-2-Mistral-7B-DPO', trust_remote_code=True)

    # Ensure the model is loaded to an appropriate device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = MistralForCausalLM.from_pretrained(
        "NousResearch/Nous-Hermes-2-Mistral-7B-DPO",
        torch_dtype=torch.float16,
        device_map="auto",  # Can be adjusted based on available hardware
        load_in_8bit=False,
        load_in_4bit=True,
        use_flash_attention_2=False,
        bnb_4bit_compute_dtype=torch.float16
    ).to(device)  # Ensure the model is sent to the correct device
    return tokenizer, model

def generate_prompts(query, filenames):

    notes = []
    for filename in filenames:
        with open(filename, 'r') as f:
            content = f.read()
            content = chunk_string(content) 
            for chunk in content:
                notes.append([filename, chunk])

    prompts = []
    for note in notes:
        prompts.append([note[0], 
        f"""
            <|im_start|>system
            {query}
            <|im_end|>
            <|im_start|>user
            {note[1]}
            <|im_start|>assistant        
        """])

    return prompts

def eval_model(prompts, tokenizer, model):

    for filename, chat in prompts:
        input_ids = tokenizer(chat, return_tensors="pt", return_attention_mask=True).to("cuda")
        generated_ids = model.generate(input_ids['input_ids'], attention_mask=input_ids["attention_mask"], max_new_tokens=40, temperature=0.1, repetition_penalty=1.1, do_sample=True, eos_token_id=tokenizer.eos_token_id)
        decoded_output = tokenizer.decode(generated_ids[0][input_ids['input_ids'].shape[-1]:], skip_special_tokens=True, clean_up_tokenization_space=True)

        print(f"File: {filename}\nResponse: {decoded_output}")


filenames = list_files_recursively(vault_dir)
query = f"""
Take the note provided below and provide a list of 5 tags representative of the content in the format:
[tag1, tag2, tag3, tag4, tag5]
"""

prompts = generate_prompts(query, filenames)

tokenizer, model = load_model()
eval_model(prompts, tokenizer, model)

del model
gc.collect()
