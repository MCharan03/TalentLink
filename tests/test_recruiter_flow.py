import pytest
from app import create_app, db
from app.models import User, RecruiterProfile, Organization

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@test.com'
    app.config['MAIL_SUPPRESS_SEND'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_recruiter_registration_flow(client):
    # 1. Submit Recruiter Request
    response = client.post('/auth/register/recruiter', data={
        'email': 'recruiter@tech.com',
        'username': 'Recruiter Bob',
        'organization_name': 'Tech Giants'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Request submitted successfully' in response.data

    # 2. Verify DB State
    user = User.query.filter_by(email='recruiter@tech.com').first()
    assert user is not None
    assert user.role == 'recruiter'
    assert user.recruiter_profile is not None
    assert user.recruiter_profile.is_verified == False
    assert user.recruiter_profile.organization.name == 'Tech Giants'

    # 3. Try to Login (Should fail/warn)
    user.set_password('knownpassword')
    db.session.commit()

    response = client.post('/auth/login', data={
        'email': 'recruiter@tech.com',
        'password': 'knownpassword'
    }, follow_redirects=True)
    
    assert b'Your account is pending approval' in response.data

    # 4. Admin Approves (Simulated via Route)
    # Create admin user first
    admin = User(username='admin', email='admin@sra.com', role='admin', is_verified=True)
    admin.set_password('adminpass')
    db.session.add(admin)
    db.session.commit()
    
    # Login as admin
    client.post('/auth/login', data={'email': 'admin@sra.com', 'password': 'adminpass'})
    
    # Approve
    profile = user.recruiter_profile
    response = client.post(f'/admin/approve_recruiter/{profile.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Recruiter Recruiter Bob approved' in response.data

    # 5. Login Success (Recruiter)
    user = User.query.filter_by(email='recruiter@tech.com').first()
    assert user.recruiter_profile.is_verified == True
    
    user.set_password('newknownpassword')
    db.session.commit()

    response = client.post('/auth/login', data={
        'email': 'recruiter@tech.com',
        'password': 'newknownpassword'
    }, follow_redirects=True)
    
    # Should redirect to recruiter dashboard
    assert b'Talent Search' in response.data or response.request.path == '/recruiter/dashboard'
