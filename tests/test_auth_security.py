import pytest
from unittest.mock import patch
from app.models import User, db
from app.utils.auth_utils import (
    generate_verification_token, confirm_verification_token,
    generate_reset_token, confirm_reset_token,
    check_rate_limit, record_failed_attempt, clear_login_attempts,
    _login_attempts
)


def test_password_strength_rejects_weak(client):
    """Registration should reject weak passwords."""
    response = client.post('/auth/register', data={
        'email': 'weak@test.com',
        'username': 'weakuser',
        'password': 'short',
        'password2': 'short',
        'csrf_token': 'test'
    }, follow_redirects=True)
    assert b'Password must be at least 8 characters' in response.data


def test_password_strength_accepts_strong(app, client):
    """Registration should accept strong passwords."""
    with app.app_context():
        response = client.post('/auth/register', data={
            'email': 'strong@test.com',
            'username': 'stronguser',
            'password': 'StrongP4ss',
            'password2': 'StrongP4ss'
        }, follow_redirects=True)
        # Should succeed and redirect to login (or show success flash)
        assert response.status_code == 200


def test_rate_limiting_locks_after_threshold():
    """Login should be locked after 5 failed attempts."""
    email = 'ratelimit@test.com'
    _login_attempts.clear()
    
    for _ in range(5):
        record_failed_attempt(email)
    
    is_locked, remaining = check_rate_limit(email)
    assert is_locked is True
    assert remaining > 0
    
    # Cleanup
    clear_login_attempts(email)


def test_rate_limiting_allows_before_threshold():
    """Login should be allowed with fewer than 5 failed attempts."""
    email = 'nolock@test.com'
    _login_attempts.clear()
    
    for _ in range(3):
        record_failed_attempt(email)
    
    is_locked, remaining = check_rate_limit(email)
    assert is_locked is False
    assert remaining == 0
    
    clear_login_attempts(email)


def test_clear_login_attempts():
    """Clearing attempts should allow login again."""
    email = 'clearme@test.com'
    _login_attempts.clear()
    
    for _ in range(5):
        record_failed_attempt(email)
    
    clear_login_attempts(email)
    is_locked, _ = check_rate_limit(email)
    assert is_locked is False


def test_verification_token_valid(app):
    """Valid verification token should return the email."""
    with app.app_context():
        email = 'verify@test.com'
        token = generate_verification_token(email)
        result = confirm_verification_token(token, max_age=3600)
        assert result == email


def test_verification_token_invalid(app):
    """Invalid token should return None."""
    with app.app_context():
        result = confirm_verification_token('invalid-token', max_age=3600)
        assert result is None


def test_reset_token_valid(app):
    """Valid reset token should return the email."""
    with app.app_context():
        email = 'reset@test.com'
        token = generate_reset_token(email)
        result = confirm_reset_token(token, max_age=1800)
        assert result == email


def test_reset_token_invalid(app):
    """Invalid reset token should return None."""
    with app.app_context():
        result = confirm_reset_token('bad-token', max_age=1800)
        assert result is None


def test_forgot_password_page(client):
    """Forgot password page should load."""
    response = client.get('/auth/forgot_password')
    assert response.status_code == 200
    assert b'Forgot Password' in response.data


def test_forgot_password_post(client, app):
    """Posting to forgot password should always show success (no email enumeration)."""
    with app.app_context():
        response = client.post('/auth/forgot_password', data={
            'email': 'nonexistent@test.com'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login with generic message


def test_unverified_user_cannot_login(app, client):
    """Unverified user should not be able to login."""
    with app.app_context():
        user = User.query.filter_by(email='user@test.com').first()
        user.is_verified = False
        db.session.commit()
        
        response = client.post('/auth/login', data={
            'email': 'user@test.com',
            'password': 'password'
        }, follow_redirects=True)
        
        assert b'verify your email' in response.data
        
        # Restore for other tests
        user.is_verified = True
        db.session.commit()


def test_verified_user_can_login(app, auth, client):
    """Verified user should be able to login."""
    with app.app_context():
        user = User.query.filter_by(email='user@test.com').first()
        user.is_verified = True
        db.session.commit()
        
        response = auth.login()
        assert response.status_code == 200
        assert b'testuser' in response.data
