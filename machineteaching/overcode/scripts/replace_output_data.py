import os
import shutil
import sys

def copy_output_data(problem_id, src_dir, dst_dir):
    """
    Copy output data (if available) for a given problem ID to the destination 'output' directory (that will be created during the copy operation).

    Args:
        problem_id (int): The ID of the problem for which data is being copied.
        src_dir (str): The source 'output' directory from which to copy the problem output data.
        dst_dir (str): The destination 'output' directory where the problem output data will be copied.

    Returns:
        None

    Raises:
        ValueError: If the source 'output' directory does not exist.
        shutil.Error: If any error occurs during the data copying process.
    """

    if not os.path.exists(src_dir):
        raise ValueError(f"Source 'output' directory '{src_dir}' does not exist.")

    try:
        shutil.copytree(src_dir, dst_dir)
    except FileNotFoundError:
        raise ValueError("Problem output data does not exist in the source directory.")
    except shutil.Error as e:
        raise shutil.Error(f"An error occurred while copying output data: {e}")

    print(f"Output data for problem {problem_id} copied to '{dst_dir}'")


def delete_output_data(dst_dir):
    """
    Delete previous output data in the destination 'output' directory.

    Args:
        dst_dir (str): The destination 'output' directory from which previous problem output data will be deleted.

    Returns:
        None

    Raises:
        shutil.Error: If any error occurs during the deletion process.
    """

    try:
        shutil.rmtree(dst_dir, ignore_errors=True)
    except shutil.Error as e:
        raise shutil.Error(f"An error occurred while deleting previous output data: {e}")

    print(f"Previous output data deleted from '{dst_dir}'")


def replace_output_data(problem_id, src_dir, dst_dir):
    """
    Replace existing output data with new output data for a given problem ID in the destination 'output' directory.

    This function performs two operations:
    1. Deletes the existing 'output' directory from the destination directory.
    2. Copies new output data to the destination 'output' directory.

    Args:
        problem_id (int): The ID of the problem for which output data is being replaced.
        src_dir (str): The source 'output' directory from which to copy the problem output data.
        dst_dir (str): The destination 'output' directory where the new problem output data will be stored.

    Returns:
        None

    Raises:
        shutil.Error: If any error occurs during the delete or copy operations.
    """

    if os.path.exists(dst_dir):
        delete_output_data(dst_dir)

    try:
        copy_output_data(problem_id, src_dir, dst_dir)
    except ValueError as ve:
        raise ValueError(f"Error: {ve}")
    except shutil.Error as se:
        raise shutil.Error(f"Error: {se}")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        problem_id = int(sys.argv[1])
        src_dir = f"../problems_data/problem_{problem_id}/output"
        dst_dir = sys.argv[2]

        try:
            replace_output_data(problem_id, src_dir, dst_dir)
        except ValueError as ve:
            print(f"Error: {ve}")
        except shutil.Error as se:
            print(f"Error: {se}")
    else:
        print("Usage: python replace_output_data.py <problem_id> <destination_directory>")


