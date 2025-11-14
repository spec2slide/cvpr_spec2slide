import os
import subprocess
import logging
import argparse

# Setup logging to record execution results to a file
log_file = 'execution_log.txt'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')


successful_executions = 0
failed_executions = 0
# Function to execute a Python file in its own directory
def execute_cleaned_file(file_path, directory):
    global successful_executions, failed_executions
    try:
        # Change to the file's directory
        original_dir = os.getcwd()  # Save the current working directory
        os.chdir(directory)  # Change to the directory where the file is located
        
        logging.info(f"Executing {file_path} in {directory}...")
        result = subprocess.run(['python', file_path], check=True, capture_output=True, text=True)
        logging.info(f"Execution output:\n{result.stdout}")
        successful_executions += 1
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing {file_path}: {e.stderr}")
        failed_executions += 1
        return False
    finally:
        os.chdir(original_dir)  # Change back to the original directory
        
def main(args):
    # Track execution statistics
    total_files = 0
    cleaned_file_name = args.cleaned_file_name
    base_dir = args.base_dir
    # Iterate through all directories and files in the base directory
    for root, dirs, files in os.walk(base_dir):
        if cleaned_file_name in files:
            cleaned_file_path = os.path.join(root, cleaned_file_name)
            total_files += 1
            execute_cleaned_file(cleaned_file_name, root)

    # Calculate execution success rate
    if total_files > 0:
        success_rate = (successful_executions / total_files) * 100
    else:
        success_rate = 0.0

    # Log the final summary
    logging.info(f"Total files processed: {total_files}")
    logging.info(f"Successful executions: {successful_executions}")
    logging.info(f"Failed executions: {failed_executions}")
    logging.info(f"Success rate: {success_rate:.2f}%")

    # Print final summary to the console as well
    print(f"Total files processed: {total_files}")
    print(f"Successful executions: {successful_executions}")
    print(f"Failed executions: {failed_executions}")
    print(f"Success rate: {success_rate:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean up the generated code')
    # Define the base directory to search through (examples/)
    parser.add_argument("--base_dir", type=str, default="examples/", help="Path to the base directory to search through.")
    # Define the cleaned file name to search for
    parser.add_argument("--cleaned_file_name", type=str, default='cleaned_Llama.py', help="Name of the cleaned file name.")
    args = parser.parse_args()
    main(args)