import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app
from app.extensions import db
from app.models import User, JobPosting, JobApplication, MockTest, MockInterview, Notification, UserData

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, JobPosting=JobPosting, JobApplication=JobApplication,
                MockTest=MockTest, MockInterview=MockInterview, Notification=Notification,
                UserData=UserData)

@app.cli.command("create-tables")
def create_tables():
    """Creates database tables from sqlalchemy models."""
    with app.app_context():
        db.create_all()
        print("Database tables created.")

if __name__ == '__main__':
    app.run()
