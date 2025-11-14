"""Calculate Reference-based and -free scores using the saved results."""

import os
import json
import argparse

def get_average(scores: list[float], weights: list[int | float] = None, scale: int = 1) -> float:
    if len(scores) == 0: return 0.0
    if weights is None:
        return sum(scores) / len(scores)
    n = [s * w * scale for s, w in zip(scores, weights)]
    d = sum(weights)
    return sum(n) / d


def calc_scores(slide_deck: str, subdir: str = None) -> dict:
    """Calculate Reference-based and -free scores for a slide deck."""
    slides_dir = [d for d in os.listdir(slide_deck) if d.startswith("slide_")]
    exec_scores = []
    based_scores = {"match": [], "text": [], "color": [], "position": []}
    free_scores = {"text": [], "image": [], "layout": [], "color": []}
    for sd in slides_dir:
        # if skip image
        num_images = len([
            d for d in os.listdir(os.path.join("..", "slidesbench", slide_deck, sd, "media"))
            if d.startswith("image_")
        ])
        skip_image = (num_images == 0)

        # ref-based eval
        if subdir is None:
            based_eval_path = os.path.join(slide_deck, sd, "ref_eval.json")
        else:
            based_eval_path = os.path.join(slide_deck, sd, subdir, "ref_eval.json")
        if not os.path.exists(based_eval_path):
            print(f"Warning: {based_eval_path} does not exist.")
            if args.skip_none:
                based_eval = {}
            else:
                based_eval = {"match": 0.0, "text": 0.0, "color": 0.0, "position": 0.0}
        else:
            based_eval = json.load(open(based_eval_path))
        for k, v in based_eval.items():
            if not isinstance(v, float): based_scores[k].append(100.0)
            else: based_scores[k].append(v)

        # ref-free eval
        free_name = "gpt_4o_feedback_canonical_eval.json"
        if subdir is None:
            free_eval_path = os.path.join(slide_deck, sd, free_name)
        else:
            free_eval_path = os.path.join(slide_deck, sd, subdir, free_name)
        if os.path.exists(free_eval_path):
            free_eval = json.load(open(free_eval_path))
        else:
            print(f"Warning: {free_eval_path} does not exist.")
            if args.skip_none:
                free_eval = {}
            else:
                free_eval = {k: {"score": 0.0} for k in ["text", "image", "layout", "color"]}
        for k, v in free_eval.items():
            if skip_image and k == "image": continue
            free_scores[k].append(v["score"])
        
        # exec eval
        if not os.path.exists(based_eval_path) and not os.path.exists(free_eval_path):
            exec_scores.append(0.0)
        else:
            exec_scores.append(100.0)

    result_dict = {
        "name": slide_deck.split('/')[-1],
        "size": len(slides_dir),
        "exec": get_average(exec_scores),
        "based_scores": {k: get_average(v) for k, v in based_scores.items()},
        "free_scores": {k: get_average(v) for k, v in free_scores.items()},
    }
    return result_dict


def viz_scores(all_result_dicts: list[dict]):
    sizes = []
    execs = []
    based_scores = {"match": [], "text": [], "color": [], "position": []}
    free_scores = {"text": [], "image": [], "layout": [], "color": []}
    for result_dict in all_result_dicts:
        print(f"[{result_dict['name']}] # {result_dict['size']:2d}")
        based_score_str = ' | '.join([
            f"{k:6s}: {v:4.1f}"
            for k, v in result_dict["based_scores"].items()
        ])
        print("Reference-based Scores:", based_score_str)
        free_score_str = ' | '.join([
            f"{k:6s}: {v:4.1f}"
            for k, v in result_dict["free_scores"].items()
        ])
        print("Reference-free Scores :", free_score_str)
        print('-' * 50)

        sizes.append(result_dict["size"])
        execs.append(result_dict["exec"])
        for k, v in result_dict["based_scores"].items():
            based_scores[k].append(v)
        for k, v in result_dict["free_scores"].items():
            free_scores[k].append(v)
    
    overall_scores = []
    avg_score = get_average(execs, weights=sizes)
    print(f"Execution Score: {avg_score:4.1f}")
    print('---')
    print("Reference-Based Scores:")
    for k, scores in based_scores.items():
        avg_score = get_average(scores, weights=sizes)
        overall_scores.append(avg_score)
        print(f"{k:10s}: {avg_score:4.1f}")
    print('---')
    print("Reference-Free Scores:")
    for k, scores in free_scores.items():
        avg_score = get_average(scores, weights=sizes, scale=20)
        overall_scores.append(avg_score)
        print(f"{k:10s}: {avg_score:4.1f}")

    print('---')
    print(f"Overall Scores: {get_average(overall_scores):4.1f}")
        

    


def main():
    slide_deck_dirs = [
        os.path.join(args.example_dir, d) 
        for d in os.listdir(args.example_dir)
    ]
    all_result_dicts = []
    for slide_deck in slide_deck_dirs:
        result_dict = calc_scores(slide_deck, subdir=args.result_subdir)
        all_result_dicts.append(result_dict)
    
    viz_scores(all_result_dicts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--example_dir", type=str, default="examples")
    parser.add_argument("--result_subdir", type=str, default=None)
    parser.add_argument("--skip_none", action="store_true")

    args = parser.parse_args()

    main()
