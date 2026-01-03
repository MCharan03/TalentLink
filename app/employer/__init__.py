from flask import Blueprint

employer = Blueprint('employer', __name__)

from . import routes
