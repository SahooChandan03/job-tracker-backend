from flask import Blueprint
from .jwt import jwt_required, get_current_user

auth_bp = Blueprint('auth', __name__)

from . import routes 