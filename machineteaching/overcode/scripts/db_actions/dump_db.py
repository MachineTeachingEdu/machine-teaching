import subprocess
import json

def create_database_dump(params, dump_filename):
    """
    Create a PostgreSQL database dump using the provided parameters.

    Args:
        params (dict): A dictionary containing database connection parameters.
        dump_filename (str): The name of the dump file to create.

    Returns:
        None
    """
    try:
        # Construct the pg_dump command
        cmd = [
            "pg_dump",
            "--host", params["host"],
            "--port", "5432",
            "--username", params["user"],
            "--dbname", params["database"],
            "--file", dump_filename,
            "--format", "custom",
            "--verbose"
        ]

        # Execute the pg_dump command
        subprocess.run(cmd, check=True)

        print(f"Database dump created as '{dump_filename}'")
    except subprocess.CalledProcessError as e:
        print(f"Error creating database dump: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Load database parameters from db_params.json
    with open("../db_params.json", "r") as f:
        params = json.load(f)

    # Specify the dump file name
    dump_filename = "db_dump.backup"

    # Call the create_database_dump function
    create_database_dump(params, dump_filename)
