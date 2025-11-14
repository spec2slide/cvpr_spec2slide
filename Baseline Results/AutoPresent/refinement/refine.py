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
    

def visual_refinement(prompt, args) -> str:
    code_path = args.existing_code
    code = open(code_path, 'r').read()
    # Get the original instruction
    instruction_path = args.instruction_path
    instruction = open(instruction_path, 'r').read()
    messages = []
    jpg_path = args.existing_slide
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
    refined_code_path = args.refined_code_path
    for i, resp in enumerate(response_list):
        print(f"Found successful visual refinement at index and saved to {refined_code_path}.")
        save_response(resp, refined_code_path)
        break


def run_visual_refinement(args):
    prompt = get_prompt(args)
    visual_refinement(prompt, args)  # Run the visual refinement for the specific directory

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch run visual refinement on multiple folders")
    parser.add_argument("--existing_slide", type=str, 
                        help="The existing slide to be refined")
    parser.add_argument("--existing_code", type=str, 
                        help="The existing code to be refined")
    parser.add_argument("--instruction_path", type=str, 
                        help="The path to the instruction to generate the slide")

    parser.add_argument("--refined_code_path", type=str, default="refined_code.py", 
                        help="The path to save the refined code")

    # Model and refinement parameters (set default values or change as needed)
    parser.add_argument("--model_name", type=str, default="gpt-4o-mini", help="Model name to use.")
    parser.add_argument("--max_tokens", type=int, default=4096, help="Max tokens to generate.")
    parser.add_argument("--num_samples", type=int, default=1, help="Number of samples to generate.")
    parser.add_argument("--refinement_type", type=str, default="fully_specified", help="Task to refine on, contains fully_specified, visual_absence, and creative_generation.")
    args = parser.parse_args()
    run_visual_refinement(args)