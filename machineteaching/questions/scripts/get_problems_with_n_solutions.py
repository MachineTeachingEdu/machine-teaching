import sys
from execute_query import execute_query


def get_problems_with_at_least_n_solutions(n):
    """
    Retrieve the IDs of problems that have at least n solutions from unique users from the database.

    Args:
        n (int): The minimum number of solutions from unique users.

    Returns:
        None
    """

    # Query problem IDs, count distinct user solutions, and filter for problems with at least n solutions
    query = f"""SELECT problem_id, COUNT(DISTINCT user_id)
                FROM questions_userlog
                GROUP BY problem_id
                HAVING COUNT(DISTINCT user_id) >= {n};"""
    problems = execute_query(query)

    # Verify data
    if problems is None or len(problems) == 0:
        print(f"Error! No problems found with at least {n} solutions from unique users!")
    else:
        for problem_id, count in problems:
            print(f"Problem ID: {problem_id}, Unique User Solution Count: {count}")

        print(f"\nTotal number of problems with at least {n} solutions from unique users: {len(problems)}")


if __name__ == "__main__":
    # Check if command line arguments exist
    if len(sys.argv) > 1:
        # Retrieve the minimum number of solutions from the command line
        n = int(sys.argv[1])
        get_problems_with_at_least_n_solutions(n)
    else:
        print("No command line arguments provided. Please provide the minimum number of solutions.")

