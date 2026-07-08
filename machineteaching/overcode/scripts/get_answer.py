import ast
import os
import sys

from overcode.scripts.execute_query import execute_query


def _is_python_function(code):
    """Return whether code is valid Python containing a function."""
    if not code or not code.strip():
        return False

    try:
        tree = ast.parse(code)
    except (SyntaxError, TypeError, ValueError):
        return False

    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        for node in ast.walk(tree)
    )


def _official_answers(problem_id):
    return execute_query(
        """
        SELECT content
        FROM questions_solution
        WHERE problem_id = %s
        ORDER BY id DESC;
        """,
        (problem_id,),
    )


def _passing_student_answers(turma_id, problem_id):
    return execute_query(
        """
        SELECT solution
        FROM questions_userlog
        WHERE user_class_id = %s
          AND problem_id = %s
          AND outcome = 'P'
          AND solution IS NOT NULL
          AND btrim(solution) <> ''
        ORDER BY timestamp DESC;
        """,
        (turma_id, problem_id),
    )


def get_answer(problem_id, dst_dir="", turma_id=None):
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

    candidates = _official_answers(problem_id)
    source = "official answer"

    code = next(
        (row[0] for row in candidates if _is_python_function(row[0])),
        None,
    )

    # Some legacy problems have an official solution in another language even
    # though their student submissions are Python. OverCode executes Python, so
    # use a passing Python submission as the reference in that case.
    if code is None and turma_id is not None:
        source = "passing student answer"
        candidates = _passing_student_answers(turma_id, problem_id)
        code = next(
            (row[0] for row in candidates if _is_python_function(row[0])),
            None,
        )

    if code is None:
        raise ValueError(
            f"No valid Python answer found for problem {problem_id}"
            + (f" in class {turma_id}" if turma_id is not None else "")
        )

    os.makedirs(dst_dir, exist_ok=True)
    filepath = os.path.join(dst_dir, "answer.py")
    with open(filepath, "w", encoding="utf-8") as answer_file:
        answer_file.write(code)

    print(f"Answer saved to '{filepath}' using {source}")

if __name__ == "__main__":
  # Check if command line arguments exist
  if len(sys.argv) > 1:
      # Retrieve the problem ID from the command line
      problem_id = int(sys.argv[1])
      get_answer(problem_id)
  else:
      print("No command line arguments provided.")
