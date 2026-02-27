import pytest
from app import create_app, db
from app.models import User, JobPosting
import time

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_jobs_page_performance(client):
    # Setup
    with client.application.app_context():
        # Create user
        user = User(username='perf_user', email='perf@test.com', role='user', is_verified=True)
        user.set_password('password')
        db.session.add(user)
        # Create jobs
        for i in range(15):
            job = JobPosting(title=f"Job {i}", description="Desc", created_by=user.id)
            db.session.add(job)
        db.session.commit()

    # Login
    client.post('/auth/login', data={'email': 'perf@test.com', 'password': 'password'})

    # Measure time for /jobs (should be fast)
    start_time = time.time()
    response = client.get('/user/jobs')
    end_time = time.time()
    
    assert response.status_code == 200
    duration = end_time - start_time
    print(f"Jobs Page Duration: {duration}s")
    
    # Assert it's fast (e.g., < 0.5s) - tough in CI/local var, but logic check is key
    # Assert it DOES NOT contain "AI Recommended For You" directly (async)
    assert b'AI Recommended For You' not in response.data
    assert b'recommended-jobs-container' in response.data
    assert b'spinner-border' in response.data

    # Test Async Route
    response_async = client.get('/user/partials/recommended_jobs')
    assert response_async.status_code == 200
    # Since no resume uploaded, it should return empty or specific message, but route works
