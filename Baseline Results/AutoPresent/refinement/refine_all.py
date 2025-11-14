import os
import argparse
from utils import encode_image, extract_code_pieces
import openai
openai.api_key = os.environ["OPENAI_API_KEY"]
client = openai.OpenAI()
    
def get_prompt(args):
    if args.refinement_type == "fully_specified":
        with open('./prompts/refinement_fully_specified.prompt', 'r') as f:
            prompt = f.read()
    elif args.refinement_type == "visual_absence":
        with open('./prompts/refinement_visual_absence.prompt', 'r') as f:
            prompt = f.read()
    else:
        with open('./prompts/refinement_creative_generation.prompt', 'r') as f:
            prompt = f.read()
    return prompt
def save_response(response: str, output_path: str):
    """Save the model response to the designated file path."""
    with open(output_path.replace('.py', '.md'), 'w') as fw: fw.write(response)
    code = extract_code_pieces(response, concat=True)
    with open(output_path, 'w') as fw: fw.write(code)
    

def visual_refinement(prompt, output_dir) -> str:
    code_path = os.path.join(output_dir, f"gpt_4o.py")
    code = open(code_path, 'r').read()
    # Get the original instruction
    instruction_path = code_path.replace("examples_gpt", "examples").replace("wlib_1/gpt_4o.py", "instruction_model.txt")
    instruction = open(instruction_path, 'r').read()
    messages = []
    jpg_path = os.path.join(output_dir, f"gpt_4o.jpg")
    if os.path.exists(jpg_path):
        image_url = f"data:image/jpeg;base64,{encode_image(jpg_path)}"
        messages += [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt.replace("INSERT_INSTRUCTION_HERE", instruction).replace("INSERT_PREV_CODE_HERE", code)},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }]
    else:
        messages += [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt.replace("INSERT_INSTRUCTION_HERE", instruction).replace("INSERT_PREV_CODE_HERE", code)}
            ],
        }]
        

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=4096,
        n=1,
    )
    print(f"Get response.")
    response_list = [c.message.content for c in response.choices]
    refined_code_path = code_path.replace(".py", "_visual_2.py").replace("wlib_1/", "")
    for i, resp in enumerate(response_list):
        print(f"Found successful visual refinement at index and saved to {refined_code_path}.")
        save_response(resp, refined_code_path)
        break



def run_visual_refinement_on_all(args):
    prompt = get_prompt(args)
    base_path = args.base_path
    for slide_deck_name in os.listdir(base_path):
        slide_deck_path = os.path.join(base_path, slide_deck_name)
        if os.path.isdir(slide_deck_path):
            for slide_i in os.listdir(slide_deck_path):
                slide_path = os.path.join(slide_deck_path, slide_i, "wlib_1/")
                if os.path.isdir(slide_path):
                    output_dir = slide_path  # Set the output directory for each iteration
                    visual_refinement(prompt, output_dir)  # Run the visual refinement for the specific directory

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch run visual refinement on multiple folders")
    parser.add_argument("--base_path", type=str, default="../slidesbench/examples_gpt",
                        help="Base directory containing slide decks (e.g., examples_gpt)")

    # Model and refinement parameters (set default values or change as needed)
    parser.add_argument("--model_name", type=str, default="gpt-4o-mini", help="Model name to use.")
    parser.add_argument("--max_tokens", type=int, default=4096, help="Max tokens to generate.")
    parser.add_argument("--num_samples", type=int, default=1, help="Number of samples to generate.")
    parser.add_argument("--refinement_type", type=str, default="fully_specified", help="Task to refine on, contains fully_specified, visual_absence, and creative_generation.")
    args = parser.parse_args()
    run_visual_refinement_on_all(args)