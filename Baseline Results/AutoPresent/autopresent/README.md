# Presenter

This repo contains the training and evaluation of the Presenter-8B

## Presenter Training

We use the training set from SlidesBench with the (instruction, code) pairs to train llama3 instruct 8B model. Then, push the trained model onto Huggingface.
```bash
python train.py --model_name "unsloth/llama-3-8b-bnb-4bit" --data_path "SlidesAgent/slidesbench/dataset.csv" --finetuned_model_name "your_path_to_save_model"
```

## Presentet Evaluation
Run the following command to use the trained model generate code for natural language instructions.
```bash
python generate.py --path "path_to_your_model" ----save_output_pth "path_to_save_model_output" --dataset_path "path_to_the_test_dataset_csv"
```
