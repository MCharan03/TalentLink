from app import create_app, db
from sqlalchemy import text
import sqlite3
import os

app = create_app()

def add_column_if_not_exists(table, column, type_def):
    try:
        with app.app_context():
            # Check if column exists using raw connection for SQLite specifics
            # Or just try to add it and catch error
            with db.engine.connect() as conn:
                try:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}"))
                    print(f"Added column {column} to {table}")
                except Exception as e:
                    if "duplicate column name" in str(e):
                        print(f"Column {column} already exists in {table}")
                    else:
                        print(f"Error adding {column}: {e}")
    except Exception as e:
        print(f"Context Error: {e}")

if __name__ == "__main__":
    db_path = os.path.join('app', 'app.db')
    if not os.path.exists(db_path):
        print("Database not found, creating new one...")
        with app.app_context():
            db.create_all()
    else:
        print("Updating existing database schema...")
        add_column_if_not_exists('users', 'google_id', 'VARCHAR(100)')
        add_column_if_not_exists('users', 'linkedin_id', 'VARCHAR(100)')
        print("Done.")
