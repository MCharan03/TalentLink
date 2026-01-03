from flask import Flask
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
