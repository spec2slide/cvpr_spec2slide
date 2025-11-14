import os
import json
import gradio

task_choice = {
    "art_photos (25)": 25,
    "business (16)": 16,
    "career (19)": 19,
    "design (6)": 6,
    "entrepreneur (11)": 11,
    "environment (10)": 10,
    "food (32)": 32,
    "marketing (43)": 43,
    "social_media (21)": 21,
    "technology (12)": 12,
}

def format_scores(scores: dict):
    text_list = []
    for metric, score in scores.items():
        text = f"{metric}: "
        if isinstance(score, dict):
            text += f"{score['score']:4.1f} ({score['justification']})"
        else:
            text += f'{score:4.1f}'
        text_list.append(text)
    return '\n'.join(text_list)
        

def viz_example(domain: str, index: int):
    domain = domain.split('(')[0].strip()
    slide_dir = os.path.join("examples", domain, f"slide_{index}")
    image_path = os.path.join(slide_dir, "gpt_4o.jpg")

    ref_based_path = os.path.join(slide_dir, "ref_eval.json")
    ref_based_scores = json.load(open(ref_based_path))
    ref_based_text = format_scores(ref_based_scores)

    ref_free_path = os.path.join(slide_dir, "gpt_4o_eval.json")
    ref_free_scores = json.load(open(ref_free_path))
    ref_free_text = format_scores(ref_free_scores)

    return (image_path, ref_based_text, ref_free_text)


demo = gradio.Interface(
    fn=viz_example, 
    inputs=[
        gradio.Dropdown(choices=list(task_choice.keys()), label="Select Task"), 
        "text",
    ], 
    outputs=[
        gradio.Image(label="Slide Image"),
        gradio.Textbox(label="Ref-based Scores"),
        gradio.Textbox(label="Ref-free Scores")
    ],
    title="GPT-4o Generation"
)

demo.launch()