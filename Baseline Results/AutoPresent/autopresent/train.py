from unsloth import FastLanguageModel
import torch
import csv
from datasets import Dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import argparse
import os
import sys
# Increase the field size limit to handle large fields
csv.field_size_limit(sys.maxsize)
HF_TOKEN = "your-hf-token"
os.environ["HF_TOKEN"] = HF_TOKEN

INSTRUCTION = """Your task is to create a slide in PPTX format by generating Python programs following the instructions.
You need to attain the images you need.

Instruction:
INSERT_INSTRUCTION_HERE"""


# 4bit pre quantized models we support for 4x faster downloading + no OOMs.
fourbit_models = [
    "unsloth/mistral-7b-bnb-4bit",
    "unsloth/mistral-7b-instruct-v0.2-bnb-4bit",
    "unsloth/llama-2-7b-bnb-4bit",
    "unsloth/gemma-7b-bnb-4bit",
    "unsloth/gemma-7b-it-bnb-4bit", # Instruct version of Gemma 7b
    "unsloth/gemma-2b-bnb-4bit",
    "unsloth/gemma-2b-it-bnb-4bit", # Instruct version of Gemma 2b
    "unsloth/llama-3-8b-bnb-4bit", # [NEW] 15 Trillion token Llama-3
] # More models at https://huggingface.co/unsloth

def formatting_prompts_func(examples):
    texts = []
    num_examples = len(examples['instruction'])
    for index in range(num_examples): 
        
        input = examples['instruction'][index]
        output = examples['code'][index]
        input = INSTRUCTION.replace('INSERT_INSTRUCTION_HERE', input)
        messages = [
            {"role": "user", "content": input },
            {"role": "assistant", "content": output},
        ]
        text = tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=False
        )
        texts.append(text)
        
    return { "text" : texts, }


def load_dataset_from_csv(file_path):
    """Load the dataset from a CSV file back into a Python dictionary."""    
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        num = 0
        dataset_rows = {'instruction': [], 'code': []}
        for row in reader:
            try:
                num += 1
                # Split the code field by newlines to count lines
                code_lines = row['code'].split('\n')
                if len(code_lines) > 400:
                    print(f"Skipping row {num} due to code exceeding 400 lines.")
                    continue  # Skip the row if code exceeds 400 lines
                dataset_rows['instruction'].append(row['instruction'])
                dataset_rows['code'].append(row['code'])
            except:
                print("Too long!")
    print(f"total is {num}")
    return Dataset.from_dict(dataset_rows)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Train and fine-tune a language model.")
    parser.add_argument("--model_name", default="meta-llama/Llama-3.1-8B-Instruct", type=str, help="Name of the pre-trained model.")
    parser.add_argument("--data_path", default="../slidesbench/dataset_train_high_level.csv", type=str, help="Path to the training data CSV file.")
    parser.add_argument("--finetuned_model_name", required=True, type=str, help="Name of the fine-tuned model.")

    args = parser.parse_args()
    max_seq_length = 2048 
    dtype = None

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = args.model_name,
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = False,
        token = HF_TOKEN
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r = 128, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 32,
        lora_dropout = 0, 
        bias = "none",    
        use_gradient_checkpointing = "unsloth", 
        random_state = 3407,
        use_rslora = False,
        loftq_config = None,
    )

    

    EOS_TOKEN = tokenizer.eos_token # Must add EOS_TOKEN

    dataset = load_dataset_from_csv(args.data_path)
    dataset = dataset.map(formatting_prompts_func, batched = True,)

    # Train model
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        packing = True, # Can make training 5x faster for short sequences.
        args = TrainingArguments(
            per_device_train_batch_size = 1,
            gradient_accumulation_steps = 2,
            warmup_steps = 20,
            max_steps = -1,
            num_train_epochs=1,
            learning_rate = 3e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "unsloth_outputs_8_shots",
            report_to="none", 
        ),
    )
    trainer_stats = trainer.train()

    # Save model to huggingface hub
    model.push_to_hub(args.finetuned_model_name, token = HF_TOKEN)
    tokenizer.push_to_hub(args.finetuned_model_name, token = HF_TOKEN)