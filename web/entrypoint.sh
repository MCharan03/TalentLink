#!/bin/bash
# Initialize the database if it doesn't exist
if [ ! -f /app/backend/data/talentlink.db ]; then
    echo "Initializing database..."
    python init_new_tables.py
    python init_skillfit_tables.py
    python seed_users.py
    echo "Database initialized."
fi

# Start the application
exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 wsgi:app
