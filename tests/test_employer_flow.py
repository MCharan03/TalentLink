import pytest
from app import create_app, db
from app.models import User, EmployerProfile, Company

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

def test_employer_registration_flow(client):
    # 1. Submit Employer Request
    response = client.post('/auth/register/employer', data={
        'email': 'recruiter@tech.com',
        'username': 'Recruiter Bob',
        'company_name': 'Tech Giants'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Request submitted successfully' in response.data

    # 2. Verify DB State
    user = User.query.filter_by(email='recruiter@tech.com').first()
    assert user is not None
    assert user.role == 'employer'
    assert user.employer_profile is not None
    assert user.employer_profile.is_verified == False
    assert user.employer_profile.company.name == 'Tech Giants'

    # 3. Try to Login (Should fail/warn)
    # We can't easily guess the random password, but even if we could, logic prevents login?
    # Actually, the logic in login route checks 'employer' role and 'is_verified'.
    # We can try to login if we mock the password check, but the user has a random password.
    # We can manually set the password to test the check.
    user.set_password('knownpassword')
    db.session.commit()

    response = client.post('/auth/login', data={
        'email': 'recruiter@tech.com',
        'password': 'knownpassword'
    }, follow_redirects=True)
    
    assert b'Your account is pending approval' in response.data

    # 4. Admin Approves (Simulated via Route)
    # Create admin user first
    admin = User(username='admin', email='admin@sra.com', role='admin')
    admin.set_password('adminpass')
    db.session.add(admin)
    db.session.commit()
    
    # Login as admin
    client.post('/auth/login', data={'email': 'admin@sra.com', 'password': 'adminpass'})
    
    # Approve
    profile = user.employer_profile
    response = client.post(f'/admin/approve_employer/{profile.id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Employer Recruiter Bob approved' in response.data

    # 5. Login Success (Employer)
    # We need to know the password generated. In real app it's emailed.
    # In test, we can't easily intercept the email content unless we mock mail.send completely and inspect args.
    # But since we generated a random password in the route, we don't know it here.
    # So for this test, we will cheat and manually set password AGAIN after approval, 
    # just to verify the 'is_verified' check passes.
    # The key is that approval route sets is_verified=True.
    
    user = User.query.filter_by(email='recruiter@tech.com').first()
    assert user.employer_profile.is_verified == True
    
    user.set_password('newknownpassword')
    db.session.commit()

    response = client.post('/auth/login', data={
        'email': 'recruiter@tech.com',
        'password': 'newknownpassword'
    }, follow_redirects=True)
    
    # Should redirect to employer dashboard
    assert b'Talent Search' in response.data or response.request.path == '/employer/dashboard'
