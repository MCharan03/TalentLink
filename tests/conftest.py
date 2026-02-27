import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from app.extensions import db
from app.models import User

@pytest.fixture(autouse=True)
def mock_ai_utils():
    with patch('app.user.routes.analyze_resume') as mock_analyze:
        mock_analyze.return_value = {
            "name": "Test User",
            "email": "test@test.com",
            "resume_score": 85,
            "predicted_field": "Data Science",
            "actual_skills": ["Python", "SQL"],
            "recommended_skills": ["Machine Learning"],
            "ai_summary": "Good resume."
        }
        
        with patch('app.user.routes.get_interview_question') as mock_q:
            mock_q.return_value = "What is Python?"
            
            with patch('app.user.routes.generate_mock_test') as mock_test:
                mock_test.return_value = {
                    "questions": [
                        {"question": "Q1", "options": ["A", "B"], "correct_answer": "A"}
                    ]
                }
                yield

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Create a test admin user
        admin = User(username='admin', email='admin@test.com', role='admin', is_verified=True)
        admin.set_password('password')
        db.session.add(admin)
        
        # Create a test normal user
        user = User(username='testuser', email='user@test.com', role='user', is_verified=True)
        user.set_password('password')
        db.session.add(user)
        
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth(client):
    class AuthActions:
        def login(self, email='user@test.com', password='password'):
            return client.post('/auth/login', data={'email': email, 'password': password}, follow_redirects=True)
        def logout(self):
            return client.get('/auth/logout')
    return AuthActions()
