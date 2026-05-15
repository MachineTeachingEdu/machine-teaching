#!/bin/bash
set -e

# Load variables from JSON file
JSON_FILE="db_params.json"
HOST=$(jq -r .host "$JSON_FILE")
DATABASE=$(jq -r .database "$JSON_FILE")
USER=$(jq -r .user "$JSON_FILE")
PASSWORD=$(jq -r .password "$JSON_FILE")

# Wait for the PostgreSQL container to be up and running
until PGPASSWORD=$PASSWORD psql -h "$HOST" -U "$USER" -d "$DATABASE" -c '\l' > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 1
done

# Create target database
PGPASSWORD=$PASSWORD createdb "$DATABASE" --host "$HOST" --username "$USER" 

# Restore the database from the backup
PGPASSWORD=$PASSWORD pg_restore /docker-entrypoint-initdb.d/db_dump.backup --host "$HOST" --username "$USER" --dbname "$DATABASE" --verbose

