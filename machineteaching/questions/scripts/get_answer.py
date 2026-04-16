import sys
import os
from execute_query import execute_query

def get_answer(problem_id, dst_dir=""):
    """
    Connects to a PostgreSQL database, executes a query to retrieve the answer for a given problem ID,
    and saves the answer to a file named 'answer.py'.

    Args:
        problem_id (int): The ID of the problem for which the answer is requested.
        dst_dir (str, optional): The destination directory where the 'answer.py' file will be created.
            If not specified, the file will be created in the current working directory.

    Returns:
        None

    Raises:
        psycopg2.Error: If an error occurs during the database connection or query execution.

    Notes:
        - The 'db_params.json' file should contain the necessary parameters for the PostgreSQL connection.
        - The 'content' column of the 'questions_solution' table in the database should store the answer as a string.

    Example:
        >>> get_answer(123, dst_dir="/path/to/directory")
        Answer saved to '/path/to/directory/answer.py'
    """

    query = f""" SELECT content
                FROM questions_solution qs
                WHERE problem_id = {problem_id};"""
    answer = execute_query(query)

    # verify data
    if answer is None:
        print("Error! No answer found!")
    else:
        filepath = os.path.join(dst_dir, "answer.py")
        # The answer code is always the last element in the list returned by the query
        code = answer[-1][0]
        with open(filepath, "w") as f:
            f.write(code)
            print(f"Answer saved to '{filepath}'")

if __name__ == "__main__":
  # Check if command line arguments exist
  if len(sys.argv) > 1:
      # Retrieve the problem ID from the command line
      problem_id = int(sys.argv[1])
      get_answer(problem_id)
  else:
      print("No command line arguments provided.")

