from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
bcrypt = Bcrypt()
socketio = SocketIO()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
oauth = OAuth()
