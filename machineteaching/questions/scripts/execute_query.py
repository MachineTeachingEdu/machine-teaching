import json
import psycopg2
import os

def execute_query(query, params=None):
    """
    Execute a query using a context manager for database connection and cursor.

    Args:
        query (str): The SQL query to execute.
        params (dict, optional): Parameters for the query.

    Returns:
        The result of the query execution.
    """
    db_params_path = os.path.join(os.path.dirname(__file__), "db_params.json")
    with open(db_params_path, "r") as f:
        db_params = json.load(f)

    # Override the database parameters with environment variables if they exist.
    db_params["host"] = os.environ.get("DB_HOST", db_params["host"])

    with psycopg2.connect(**db_params) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
