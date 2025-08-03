from flask import Flask
from flask_cors import CORS
from .config.database import db
from .auth import auth_bp
from .routers import graphql_bp
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(graphql_bp, url_prefix='/graphql')
    
    # GraphQL endpoint
    from .main import graphql_handler
    app.add_url_rule('/graphql', view_func=graphql_handler, methods=['POST'])
    
    return app 