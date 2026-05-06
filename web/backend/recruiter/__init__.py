from flask import Blueprint

recruiter = Blueprint('recruiter', __name__)

from . import routes
