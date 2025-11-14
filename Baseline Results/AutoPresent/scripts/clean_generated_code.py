import os
import re
import argparse
title = """
from SlidesLib import *
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
"""
# Define a more flexible regex pattern to match the generate_presentation function
# It now matches both with or without parameters (image_path or none)
code_block_pattern = re.compile(r"```python([\s\S]+?)```")
# Function to extract and clean code from the file
def extract_code(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Search for the code block using the regex pattern
    match = code_block_pattern.search(content)
    if match:
        return match.group(0).replace("```python", "").replace("```", "")
        # If not found, just return the file content
    content = content.replace("```python", "").replace("```", "")
    content = content.replace("image_0", "media/image_0")
    content = content.replace("image_1", "media/image_1")
    content = content.replace("image_2", "media/image_2")
    content = content.replace("image_3", "media/image_3")
    content = content.replace("image_4", "media/image_4")
    content = content.replace("image_5", "media/image_5")
    content = content.replace("image_6", "media/image_6")
    content = content.replace("image_7", "media/image_7")
    content = content.replace("image_8", "media/image_8")
    content = content.replace("image_9", "media/image_9")
    content = content.replace("image_10", "media/image_10")
    return content

def extract_code_direct(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    code_title = "\ndef generate_presentation(output_pptx):\n"
    content = code_title + "    " + content + "\ngenerate_presentation('presentation.pptx')"
    content = content.replace("image_0", "media/image_0")
    content = content.replace("image_1", "media/image_1")
    content = content.replace("image_2", "media/image_2")
    content = content.replace("image_3", "media/image_3")
    content = content.replace("image_4", "media/image_4")
    content = content.replace("image_5", "media/image_5")
    content = content.replace("image_6", "media/image_6")
    content = content.replace("image_7", "media/image_7")
    content = content.replace("image_8", "media/image_8")
    content = content.replace("image_9", "media/image_9")
    content = content.replace("image_10", "media/image_10")
    return content
# Function to write the cleaned code to a new file

def extract_code_new_lib(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    # Search for the code block using the regex pattern
    match = code_block_pattern.search(content)
    if match:
        content = match.group(0).replace("```python", "").replace("```", "")
        # If not found, just return the file content
    content = content.replace("```python", "").replace("```", "").replace("from library import", "from mysearchlib import")
    content = content.replace("image_0", "media/image_0")
    content = content.replace("image_1", "media/image_1")
    content = content.replace("image_2", "media/image_2")
    content = content.replace("image_3", "media/image_3")
    content = content.replace("image_4", "media/image_4")
    content = content.replace("image_5", "media/image_5")
    content = content.replace("image_6", "media/image_6")
    content = content.replace("image_7", "media/image_7")
    content = content.replace("image_8", "media/image_8")
    content = content.replace("image_9", "media/image_9")
    content = content.replace("image_10", "media/image_10")
    return content
# Function to write

def write_cleaned_code(file_path, cleaned_code):
    # Create the new cleaned filename
    dir_name, original_file_name = os.path.split(file_path)
    cleaned_file_name = f"cleaned_{original_file_name}"
    cleaned_file_path = os.path.join(dir_name, cleaned_file_name)
    
    # Write the cleaned code to the new file
    with open(cleaned_file_path, 'w') as cleaned_file:
        cleaned_code = cleaned_code.replace("presentation.pptx", f"{original_file_name}_presentation.pptx")
        cleaned_code = cleaned_code.replace("output.pptx", f"{original_file_name}_presentation.pptx")
        cleaned_file.write(title + cleaned_code)
    
    print(f"Cleaned code written to: {cleaned_file_path}")

def main(args):
    # Iterate through all directories and files in the base directory
    target_file_name = args.target_file
    for root, dirs, files in os.walk(args.base_dir):
        if target_file_name in files:
            file_path = os.path.join(root, target_file_name)
            extracted_code = extract_code_new_lib(file_path)
            
            if extracted_code:
                print(f"Extracted code from {file_path}")
                write_cleaned_code(file_path, extracted_code)
            else:
                print(f"No code block found in {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean up the generated code')
    # Define the base directory to search through (examples/)
    parser.add_argument("--base_dir", type=str, default="examples/", help="Path to the base directory to search through.")
    # Define the target file name
    parser.add_argument("--target_file", type=str, default='Llama.py', help="Name of the target file name.")
    args = parser.parse_args()
    main(args)