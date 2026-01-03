from app import create_app
from app.utils.gamification import init_default_quests

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        print("Initializing standard quests...")
        init_default_quests()
        print("Done.")
