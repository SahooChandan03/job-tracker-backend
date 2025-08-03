from flask import Blueprint

graphql_bp = Blueprint('graphql', __name__)

from . import graphql_routes 