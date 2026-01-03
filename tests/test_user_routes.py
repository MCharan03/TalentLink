import pytest

def test_dashboard_access_denied_without_login(client):
    response = client.get('/user/dashboard', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_login_success(auth, client):
    response = auth.login()
    assert response.status_code == 200
    # Assuming redirect to index or dashboard
    assert b'testuser' in response.data

def test_resume_analysis_page(auth, client):
    auth.login()
    response = client.get('/user/resume_analysis')
    assert response.status_code == 200
    assert b'Analysis' in response.data

def test_resume_builder_page(auth, client):
    auth.login()
    response = client.get('/user/resume_builder')
    assert response.status_code == 200
    assert b'Editor' in response.data # Check for our new layout text
    assert b'Resume Preview' in response.data or b'prev-name' in response.data

def test_mock_interview_page(auth, client):
    auth.login()
    response = client.get('/user/mock_interview')
    assert response.status_code == 200
    assert b'AI Interview Session' in response.data
