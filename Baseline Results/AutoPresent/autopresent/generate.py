import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import Dataset
from unsloth import FastLanguageModel
import os
import argparse
import csv
HF_TOKEN = "your-hf-token"
os.environ["HF_TOKEN"] = HF_TOKEN
# Get prompt
INSTRUCTION = """Your task is to create a slide in PPTX format by generating Python programs following the instructions.
You can use the provided images.

Instruction:
INSERT_INSTRUCTION_HERE"""
def get_dataset(dataset_path):
    """Return the Dataset"""
    # Load the dataset 
    file_path = dataset_path
    """Load the dataset from a CSV file back into a Python dictionary."""   
    transformed_examples = [] 
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            dataset_row = {'model_input': INSTRUCTION.replace("INSERT_INSTRUCTION_HERE", row['instruction']), 'slide_folder': row['slide_folder']}
            transformed_examples.append(dataset_row)
            
    transformed_test_dataset = Dataset.from_pandas(pd.DataFrame(transformed_examples))
    return transformed_test_dataset
    
def eval(path, save_pth, dataset_path):
    # Get the eval dataset
    transformed_test_dataset = get_dataset(dataset_path)
    # Get the output from the model
    all_inputs = [input_data["model_input"] for input_data in transformed_test_dataset]
    all_paths = [input_data["slide_folder"] for input_data in transformed_test_dataset]
    
    model_id = path
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    for i in range(0, len(all_inputs)):
        batch_inputs = all_inputs[i]
        batch_paths = all_paths[i]
        messages = [
            {"role": "user", "content": batch_inputs},
        ]
        
        input_ids = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)
        
        terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = model.generate(
            input_ids,
            max_new_tokens=2048,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
        )
        response = outputs[0][input_ids.shape[-1]:]
        batch_outputs = tokenizer.decode(response, skip_special_tokens=True)
        save_folder = batch_paths
        save_path_slide = os.path.join(save_folder, save_pth)
        try:
            with open(save_path_slide, 'w') as f:
                f.write(batch_outputs)
                print("save successfully to", save_path_slide)
        except:
            print("save failed to", save_path_slide)

    
def main(args):
    eval(path=args.path, save_pth=args.save_output_pth, dataset_path=args.dataset_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the model.")
    parser.add_argument("--path", type=str, required=True, help="Path to the trained model.")
    parser.add_argument("--save_output_pth", default="presenter.py", type=str, help="Name of the py file to save the output of the model.")
    parser.add_argument("--dataset_path", default="../slidesbench/dataset_test_high_level.csv", type=str, help="Name of the py file to save the output of the model.")
    args = parser.parse_args()
    main(args)
    