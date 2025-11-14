# GPT-4o Experiments

## Generating Entier Slide Decks

```bash
# sufficient instruction setting
python create_slide_deck.py --slide_deck "art_photos" --setting "perfect"

# visual absence setting
python create_slide_deck.py --slide_deck "art_photos" --setting "visual"

# creative generation setting
python create_slide_deck.py --slide_deck "art_photos" --setting "creative"
```

## Setting 1: Detailed Instructions + Provided Image

Running with raw `python-pptx` library functions:

```bash
python create_slide.py \
--example_dir ../slidesbench/{slide_deck}/slide_{id}
```

Running with our expert-designed library functions:

```bash
python create_slide.py \
--example_dir ../slidesbench/{slide_deck}/slide_{id} \
--output_name "gpt_4o_wlib" \
--action_path "library/library_basic.txt"
```

## Setting 2: Detailed Instructions + No Image

Running with raw `python-pptx` library functions:

```bash
python create_slide.py \
--example_dir ../slidesbench/{slide_deck}/slide_{id} \
--instruction_name "instruction_no_image.txt" \
--output_name "no_image" \
--no_image
```

Running with our expert-designed library functions:

```bash
python create_slide.py \
--example_dir ../slidesbench/{slide_deck}/slide_{id} \
--instruction_name "instruction_no_image.txt" \
--output_name "no_image" \
--no_image \
--action_path "library/library.txt" # or "library/library_image.txt"
```

## Setting 3: High-Level Instructions + No Image

Running with raw `python-pptx` library functions:

```bash
python create_slide.py \
--example_dir ../slidesbench/{slide_deck}/slide_{id} \
--instruction_name "instruction_high_level.txt" \
--output_name "high_level" \
--no_image
```

Running with our expert-designed library functions:

```bash
python create_slide.py \
--example_dir ../slidesbench/{slide_deck}/slide_{id} \
--instruction_name "instruction_high_level.txt" \
--output_name "high_level" \
--no_image \
--action_path "library/library.txt" # or "library/library_image.txt"
```

## Visualize The Reuslts

We support a gradio demo to visualize model generation results. To run the visualization tool:

```bash
cd baseline
python viz.py
```

Your terminal will pop up the url where the interactive demo is hosted (e.g., http://127.0.0.1:7860). You can then paste the url to your browser to see the demo.

On this page, select the slide deck from the dropdown menu, and specify the page number on the left, the generated slide and the evaluation scores will be displayed on the right.
