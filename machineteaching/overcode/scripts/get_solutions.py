import sys
import os
import shutil
from overcode.scripts.execute_query import execute_query


def create_solutions(data, dst_dir=""):
    """
    Generate Python files for each solution in the given data.

    Args:
        data (list): A list of tuples containing the solution code and user ID.
            Each tuple should have two elements: the solution code as a string, and the user ID as an identifier.
        dst_dir (str, optional): The destination directory where the 'data' folder containing the Python files will be created.
            If not specified, the 'data' folder will be created in the current working directory.

    Returns:
        None

    Example:
        >>> solutions = [('def foo(x):\\n    return x * 2', 'user_1'), ('def bar(x):\\n    return x + 10', 'user_2')]
        >>> create_solutions(solutions, dst_dir="/path/to/directory")
        Python files for each solution saved to '/path/to/directory/data'
    """

    dir = os.path.join(dst_dir, "data")

    # Remove 'data' folder if it exists
    if os.path.exists(dir):
        shutil.rmtree(dir)

    # Create 'data' folder
    os.makedirs(dir)

    # Create Python files for each solution
    for code, user_id in data:
        with open(os.path.join(dir, f"{user_id}.py"), "w") as f:
            f.write(code)
    print(f"Python files for each solution saved to '{dir}'")


def get_solutions(turma_id, problem_id, dst_dir=""):
    """
    Retrieve the most recent solutions for a given problem ID from the database and generate Python files.

    Args:
        problem_id (int): The ID of the problem for which solutions are requested.
        dst_dir (str, optional): The destination directory where the 'data' folder containing the Python files will be created.
            If not specified, the 'data' folder will be created in the current working directory.

    Returns:
        None

    Raises:
        psycopg2.Error: If an error occurs during the database connection or query execution.

    Notes:
        - The 'db_params.json' file should contain the necessary parameters for the PostgreSQL connection.
        - The 'questions_userlog' table in the database should store the user-submitted solutions along with timestamps.
        - The function retrieves the most recent solution for each user by ordering submissions based on timestamps.

    Example:
        >>> get_solutions(123, dst_dir="/path/to/directory")
        Python files for each solution saved to '/path/to/directory/data'
    """

    # Query solutions and user IDs, getting only the most recent solution for each user
    query = f"""SELECT solution, user_id
                FROM (
                    SELECT solution, user_id,
                        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) AS rn
                    FROM questions_userlog
                    WHERE problem_id = {problem_id} AND user_class_id = {turma_id}
                ) AS submissions
                WHERE rn = 1;"""
    solutions = execute_query(query)

    # Verify data
    if solutions is None:
        print("Error! No solutions found!")
    else:
        create_solutions(solutions, dst_dir)


if __name__ == "__main__":
    # Check if command line arguments exist
    if len(sys.argv) > 1:
        # Retrieve the problem ID from the command line
        problem_id = int(sys.argv[1])
        get_solutions(problem_id)
    else:
        print("No command line arguments provided.")
