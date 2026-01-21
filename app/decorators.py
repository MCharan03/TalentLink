from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


def employer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['employer', 'admin']:
            abort(403)
        # Additional check: If employer, must be verified
        if current_user.role == 'employer':
            if not current_user.employer_profile or not current_user.employer_profile.is_verified:
                abort(403)
        return f(*args, **kwargs)
    return decorated_function
