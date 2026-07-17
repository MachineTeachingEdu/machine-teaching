import os

import psycopg2


def _database_config():
    """Build a psycopg2 connection config from the Django DB environment."""
    config = {
        "host": os.getenv("DB_HOST"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT", "5432"),
    }

    missing = [name for name, value in config.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing database configuration: " + ", ".join(missing)
        )

    return config


def execute_query(query, params=None):
    """
    Execute a query using a context manager for database connection and cursor.

    Args:
        query (str): The SQL query to execute.
        params (dict, optional): Parameters for the query.

    Returns:
        The result of the query execution.
    """
    with psycopg2.connect(**_database_config()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
