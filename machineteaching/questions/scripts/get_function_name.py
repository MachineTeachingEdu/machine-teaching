import sys
import re

def get_function_name(file_path):
    """
    Get the function name from a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        str: The extracted function name.
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Regular expression pattern to match function definitions
    pattern = r"def\s+([^(]+)\(.*\):"

    # Search for the pattern and extract the function name
    match = re.search(pattern, content)
    if match:
        function_name = match.group(1)
        return function_name
    else:
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        function_name = get_function_name(file_path)
        if function_name:
            print("Extracted function name:", function_name)
        else:
            print("Function name not found in the file.")
    else:
        print("Usage: python get_function_name.py <file_path>")
