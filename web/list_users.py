from backend import create_app, db
from backend.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"Username: {u.username}, Email: {u.email}, Role: {u.role}")
