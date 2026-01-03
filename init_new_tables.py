from app import create_app, db
from app.models import UserXP, Quest, UserQuest, GitHubProfile

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        print("Creating new tables...")
        db.create_all()
        print("Tables created successfully.")
