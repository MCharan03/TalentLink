from app import create_app, db
from sqlalchemy import text

app = create_app()

def update_schema():
    with app.app_context():
        print("Adding 'notes' column to 'job_applications'...")
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE job_applications ADD COLUMN notes TEXT"))
                conn.commit()
                print("Added 'notes' column.")
            except Exception as e:
                print(f"Note: {e}")
        print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
