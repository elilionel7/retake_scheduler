#!/usr/bin/env bash
set -e

HOST="${DB_HOST:-db}"
PORT="${DB_PORT:-5432}"

# Function to handle errors
error_exit() {
  echo "$1" 1>&2
  exit 1
}

echo "Waiting for Postgres at $HOST:$PORT..."

until nc -z "$HOST" "$PORT"; do
  sleep 1
done

echo "Postgres is ready!"

# Check if the migrations folder exists
if [ ! -d "migrations" ]; then
  echo "Initializing migrations folder..."
  flask db init || error_exit "Error initializing migrations folder"

  echo "Creating the first migration..."
  flask db migrate -m "Initial migration" || error_exit "Error creating the first migration"
fi

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade || error_exit "Error applying database migrations"

# Seed the database if not already seeded
if [ ! -f "seeded" ]; then
  echo "Seeding the database with sample data..."
  python scripts/seed.py || error_exit "Failed to seed the database."

  # Create a file to indicate seeding is done
  echo "Database seeded." 
else
  echo "Database already seeded. Skipping seeding."
fi

# Start your Flask app with Gunicorn
echo "Starting the Flask app..."
exec gunicorn wsgi:app --bind 0.0.0.0:8000
