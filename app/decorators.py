from functools import wraps
from flask import abort, request, render_template
from flask_login import current_user
from app.models import SystemSetting
from app.utils.homeostasis import Homeostasis


def self_healing_gate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check Global Maintenance Mode
        if SystemSetting.get_setting('maintenance_mode') == 'true':
            # Only admins can bypass maintenance mode (if they are logged in)
            if not (current_user.is_authenticated and current_user.role == 'admin'):
                return render_template('errors/500.html', 
                                     message="System in stasis for self-repair. Access restricted."), 503

        # 2. Check if this specific route is "sick"
        route = request.endpoint or request.path
        if Homeostasis.is_route_sick(route):
            # ALLOW ADMINS TO BYPASS ROUTE-SPECIFIC BLOCKS
            if current_user.is_authenticated and current_user.role == 'admin':
                print(f"DEBUG: Route {route} is sick but ADMIN is bypassing.", flush=True)
                return f(*args, **kwargs)
            
            print(f"DEBUG: Route {route} is blocked (sick) for non-admin.", flush=True)
            return render_template('errors/500.html', 
                                 message=f"Neural path '{route}' is unstable. Rerouting to safe sub-routines."), 503

        print(f"DEBUG: Route {route} is healthy or admin-bypass.", flush=True)
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    @self_healing_gate
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


def recruiter_required(f):
    @wraps(f)
    @self_healing_gate
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['recruiter', 'admin']:
            abort(403)
        # Additional check: If recruiter, must be verified
        if current_user.role == 'recruiter':
            if not current_user.recruiter_profile or not current_user.recruiter_profile.is_verified:
                abort(403)
        return f(*args, **kwargs)
    return decorated_function
