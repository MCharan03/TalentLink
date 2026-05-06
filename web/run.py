import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from backend.models import User, JobPosting, JobApplication, MockTest, MockInterview, Notification, UserData
from backend.extensions import db
from backend import create_app


app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, JobPosting=JobPosting, JobApplication=JobApplication,
                MockTest=MockTest, MockInterview=MockInterview, Notification=Notification,
                UserData=UserData)


if __name__ == '__main__':
    from backend.extensions import socketio
    # Reloader disabled to prevent [WinError 10038] socket issues on Windows
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
