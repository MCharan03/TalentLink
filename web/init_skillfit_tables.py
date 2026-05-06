from backend import create_app, db
from backend.models import SkillFitAssessment

app = create_app()

def init_tables():
    with app.app_context():
        print("Creating new tables for AI SkillFit...")
        db.create_all()
        print("Done.")

if __name__ == "__main__":
    init_tables()
