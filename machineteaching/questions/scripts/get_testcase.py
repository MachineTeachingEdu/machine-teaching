import sys
import os
from execute_query import execute_query


def create_testcase(data, function_name, dst_dir=""):
    """
    Create a 'testCase.py' file with 'print(function_name(...))' statements for each string in the data.

    Args:
        data (list): A list of tuples containing strings, from which the arguments for the function will be extracted.
        function_name (str): The name of the function to be applied to each string in the data.
        dst_dir (str, optional): The destination directory where the 'testCase.py' file will be created.
            If not specified, the file will be created in the current working directory.

    Returns:
        None
    """
    filepath = os.path.join(dst_dir, "testCase.py")
    with open(filepath, "w") as f:
        for item in data:
            # remove the initial and final brackets from the list of args
            string = item[0][1:-1]
            f.write(f"print({function_name}({string}))\n")

    print(f"Test cases saved to '{filepath}'")


def get_testcase(problem_id, dst_dir=""):
    """
    Retrieve test cases and function name from the database for a given problem ID,
    and create test cases using the `create_testcase` function.

    Args:
        problem_id (int): The ID of the problem for which the test cases and function name are retrieved.
        dst_dir (str, optional): The destination directory where the 'testCase.py' file will be created.
            If not specified, the file will be created in the current working directory.

    Returns:
        None
    """

    # Query test cases
    query = f"""SELECT content
                FROM questions_testcase qt
                WHERE problem_id = {problem_id};"""
    testcases = execute_query(query)

    # Query function name
    query = f"""SELECT header
                FROM questions_solution qs
                WHERE problem_id = {problem_id};"""
    function_name = execute_query(query)

    # Verify data
    if testcases is None:
        print("Error! No test cases found!")
    elif function_name is None:
        print("Error! No function name found!")
    else:
        # The function name is always the last element in the list returned by the query
        create_testcase(testcases, function_name[-1][0], dst_dir)


if __name__ == "__main__":
    # Check if command line arguments exist
    if len(sys.argv) > 1:
        # Retrieve the problem ID from the command line
        problem_id = int(sys.argv[1])
        get_testcase(problem_id)
    else:
        print("No command line arguments provided.")

