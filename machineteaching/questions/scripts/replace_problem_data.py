import sys
import os
import shutil
import json


def copy_problem_data(problem_id, dst_dir):
    """
    Copy data (answer, testCase, and solutions) for a given problem ID to the destination directory.

    Args:
        problem_id (int): The ID of the problem for which data is being copied.
        dst_dir (str): The destination directory where the problem data will be copied.

    Returns:
        None

    Raises:
        ValueError: If the source directory (../problems_data/problem_<problem_id>) does not exist.
        ValueError: If the destination directory does not exist.
        ValueError: If the problem data does not exist in the source directory.
        shutil.Error: If any error occurs during the data copying process.

    Example:
        >>> copy_problem_data(737, "/path/to/destination/directory")
        Data for problem 737 copied to '/path/to/destination/directory'
    """

    # Source directory for the problem data
    src_dir = f"../problems_data/problem_{problem_id}"

    # Check if the source directory exists
    if not os.path.exists(src_dir):
        raise ValueError(f"Source directory '{src_dir}' does not exist.")

    # Check if the destination directory exists
    if not os.path.exists(dst_dir):
        raise ValueError(f"Destination directory '{dst_dir}' does not exist.")

    # Copy problem solutions (data directory) to the destination directory
    try:
        # Copy 'output' directory if it exists in the source directory
        if os.path.exists(os.path.join(src_dir, "output")):
            shutil.copytree(os.path.join(src_dir, "output"), os.path.join(dst_dir, "output"))

        # Copy 'data' directory to the destination directory
        shutil.copytree(os.path.join(src_dir, "data"), os.path.join(dst_dir, "data"))

        # Copy 'answer.py' to the 'data' folder in the destination directory
        shutil.copy(os.path.join(src_dir, "answer.py"), os.path.join(dst_dir, "data", "answer.py"))

        # Copy 'testCase.py' to the destination directory
        shutil.copy(os.path.join(src_dir, "testCase.py"), os.path.join(dst_dir, "testCase.py"))
        
    except FileNotFoundError:
        raise ValueError("Problem data does not exist in the source directory.")
    except shutil.Error as e:
        raise shutil.Error(f"An error occurred while copying data: {e}")

    print(f"Data for problem {problem_id} copied to '{dst_dir}'")


def delete_problem_data(dst_dir):
    """
    Delete previous problem data in the destination directory.

    Args:
        dst_dir (str): The destination directory where the problem data is stored.

    Returns:
        None

    Raises:
        ValueError: If the destination directory does not exist.
        shutil.Error: If any error occurs during the deletion process.

    Example:
        >>> delete_problem_data("/path/to/destination/directory")
        Previous problem data deleted from '/path/to/destination/directory'
    """

    # Check if the destination directory exists
    if not os.path.exists(dst_dir):
        raise ValueError("Destination directory does not exist.")

    # Delete 'data', 'output' and 'testCase.py' from the destination directory if they exist
    try:
        if os.path.exists(os.path.join(dst_dir, "data")):
            shutil.rmtree(os.path.join(dst_dir, "data"))

        if os.path.exists(os.path.join(dst_dir, "testCase.py")):
            os.remove(os.path.join(dst_dir, "testCase.py"))

        if os.path.exists(os.path.join(dst_dir, "output")):
            shutil.rmtree(os.path.join(dst_dir, "output"))

    except shutil.Error as e:
        raise shutil.Error(f"An error occurred while deleting previous problem data: {e}")

    print(f"Previous problem data deleted from '{dst_dir}'")


def replace_problem_data(problem_id, dst_dir):
    """
    Replace existing problem data with new data for a given problem ID in the destination directory.

    This function performs two operations:
    1. Deletes the existing 'data' and 'output' directories and 'testCase.py' file from the destination directory.
    2. Copies new problem data (answer.py, testCase.py, data, and output) to the destination directory.

    Args:
        problem_id (int): The ID of the problem for which data is being replaced.
        dst_dir (str): The destination directory where the new problem data will be stored.

    Returns:
        None

    Raises:
        ValueError: If the destination directory does not exist.
        shutil.Error: If any error occurs during the delete or copy operations.

    Example:
        >>> replace_problem_data(737, "/path/to/destination/directory")
        Data for problem 737 replaced in '/path/to/destination/directory'
    """

    # Check if the destination directory exists
    if not os.path.exists(dst_dir):
        raise ValueError("Destination directory does not exist.")

    # Delete previous problem data in the destination directory
    delete_problem_data(dst_dir)

    # Copy new data for the given problem to the destination directory
    try:
        copy_problem_data(problem_id, dst_dir)
    except ValueError as ve:
        raise ValueError(f"Error: {ve}")
    except shutil.Error as se:
        raise shutil.Error(f"Error: {se}")

    print(f"Data for problem {problem_id} replaced in '{dst_dir}'")


if __name__ == "__main__":
    # Check if command line arguments exist
    if len(sys.argv) > 2:
        # Retrieve the problem ID and destination directory from the command line
        problem_id = int(sys.argv[1])
        dst_dir = sys.argv[2]

        # Replace existing problem data with new data
        try:
            replace_problem_data(problem_id, dst_dir)
        except ValueError as ve:
            print(f"Error: {ve}")
        except shutil.Error as se:
            print(f"Error: {se}")
    else:
        print("Usage: python replace_problem_data.py <problem_id> <destination_directory>")

