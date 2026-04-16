import sys
from execute_query import execute_query


def get_problems_with_at_least_n_and_m_solutions(n, m):
    """
    Retrieve the IDs of problems that have at least n solutions and m correct solutions from unique users from the database.

    Args:
        n (int): The minimum number of solutions from unique users.
        m (int): The minimum number of correct solutions from unique users.

    Returns:
        None
    """
    # Query problem IDs, count distinct user solutions, and filter for problems with at least n solutions and m correct solutions
    query = f"""
                SELECT problem_id, COUNT(DISTINCT user_id) AS total_solutions, COUNT(DISTINCT CASE WHEN outcome = 'P' THEN user_id ELSE NULL END) AS correct_solutions
                FROM questions_userlog
                GROUP BY problem_id
                HAVING COUNT(DISTINCT user_id) >= {n} AND COUNT(DISTINCT CASE WHEN outcome = 'P' THEN user_id ELSE NULL END) >= {m};
            """
    problems = execute_query(query)

    # Verify data
    if problems is None or len(problems) == 0:
        print(f"Error! No problems found with at least {n} solutions and {m} correct solutions from unique users!")
    else:
        for problem_id, total_solutions, correct_solutions in problems:
            print(f"Problem ID: {problem_id}, Total Unique User Solution Count: {total_solutions}, Correct Solution Count: {correct_solutions}")

        print(f"\nTotal number of problems with at least {n} solutions and {m} correct solutions from unique users: {len(problems)}")


if __name__ == "__main__":
    # Check if command line arguments exist
    if len(sys.argv) > 2:
        # Retrieve the minimum number of total and correct solutions from the command line
        n = int(sys.argv[1])
        m = int(sys.argv[2])
        get_problems_with_at_least_n_and_m_solutions(n, m)
    else:
        print("No command line arguments provided. Please provide the minimum number of total solutions and correct solutions.")
