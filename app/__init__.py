from flask import Flask, render_template, request, abort
from .config import config
from .extensions import db, login_manager, bcrypt, socketio, migrate, mail, csrf, oauth


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, async_mode='threading')
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    oauth.init_app(app)

    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .employer import employer as employer_blueprint
    app.register_blueprint(employer_blueprint, url_prefix='/employer')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.context_processor
    def inject_system_status():
        from .utils.homeostasis import Homeostasis
        from flask_login import current_user
        from .models import UserXP
        
        status = Homeostasis.get_system_status()
        energy = 100
        if current_user.is_authenticated:
            xp_profile = UserXP.query.filter_by(user_id=current_user.id).first()
            if xp_profile:
                energy = xp_profile.energy
        
        return dict(system_status=status, user_energy=energy)

    @app.errorhandler(500)
    def internal_error(error):
        from .utils.homeostasis import Homeostasis
        from flask import request
        Homeostasis.log_error(request.endpoint or request.path, str(error))
        return render_template('errors/500.html'), 500

    @app.before_request
    def check_maintenance_mode():
        from .models import SystemSetting
        from flask import request, render_template, abort
        from flask_login import current_user
        
        # Bypass for static files
        if request.path.startswith('/static'):
            return

        if SystemSetting.get_setting('maintenance_mode') == 'true':
            # Allow admins to access during maintenance
            is_admin = current_user.is_authenticated and current_user.role == 'admin'
            if not is_admin and request.endpoint != 'auth.logout' and 'login' not in request.path:
                return render_template('errors/500.html', 
                                     message="System in stasis for self-repair. Access restricted."), 503

    # User loader and context processors
    from .models import User, Notification
    from sqlalchemy import desc

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_notifications():
        return dict(Notification=Notification, desc=desc)

    # Register SocketIO events
    with app.app_context():
        from . import socket_events

    return app

