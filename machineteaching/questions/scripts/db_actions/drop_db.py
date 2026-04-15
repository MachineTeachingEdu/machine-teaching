import json
import subprocess

# Load database parameters from db_params.json
with open("../db_params.json", "r") as f:
    db_params = json.load(f)

# Extract parameters
host = db_params["host"]
port = "5432"
username = db_params["user"]
password = db_params["password"]
dbname = db_params["database"]

# Drop the target database
drop_db_command = [
    "dropdb",
    dbname,
    "-h", host,
    "-p", port,
    "-U", username,
    "--no-password",
    "--if-exists"
]
subprocess.run(drop_db_command)
