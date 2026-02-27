"""
Auth utility functions for token-based email verification, password reset,
and rate limiting.
"""
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app
from datetime import datetime
from collections import defaultdict
import time


# --- Token Generation & Verification ---

def _get_serializer():
    """Returns a URLSafeTimedSerializer using the app's SECRET_KEY."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def generate_verification_token(email):
    """Generate a timed token for email verification."""
    s = _get_serializer()
    return s.dumps(email, salt='email-verification')


def confirm_verification_token(token, max_age=3600):
    """
    Confirm an email verification token.
    Returns the email if valid, None if expired or invalid.
    max_age: token validity in seconds (default 1 hour).
    """
    s = _get_serializer()
    try:
        email = s.loads(token, salt='email-verification', max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None


def generate_reset_token(email):
    """Generate a timed token for password reset."""
    s = _get_serializer()
    return s.dumps(email, salt='password-reset')


def confirm_reset_token(token, max_age=1800):
    """
    Confirm a password reset token.
    Returns the email if valid, None if expired or invalid.
    max_age: token validity in seconds (default 30 minutes).
    """
    s = _get_serializer()
    try:
        email = s.loads(token, salt='password-reset', max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None


# --- Rate Limiting ---

# In-memory store for login attempts: {email: [(timestamp, ...),]}
_login_attempts = defaultdict(list)
_LOCKOUT_THRESHOLD = 5
_LOCKOUT_DURATION = 900  # 15 minutes in seconds


def check_rate_limit(email):
    """
    Check if login is rate-limited for a given email.
    Returns (is_locked, remaining_seconds).
    """
    now = time.time()
    # Clean old attempts
    _login_attempts[email] = [
        ts for ts in _login_attempts[email] 
        if now - ts < _LOCKOUT_DURATION
    ]
    
    if len(_login_attempts[email]) >= _LOCKOUT_THRESHOLD:
        oldest = _login_attempts[email][0]
        remaining = int(_LOCKOUT_DURATION - (now - oldest))
        return True, remaining
    
    return False, 0


def record_failed_attempt(email):
    """Record a failed login attempt."""
    _login_attempts[email].append(time.time())


def clear_login_attempts(email):
    """Clear failed attempts after successful login."""
    _login_attempts.pop(email, None)
