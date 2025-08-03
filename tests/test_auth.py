import pytest
from app import create_app
from app.config.database import db
from app.models import User
from passlib.hash import bcrypt

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_register_user(client):
    """Test user registration"""
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'access_token' in data
    assert data['user']['email'] == 'test@example.com'

def test_login_user(client):
    """Test user login"""
    # First register a user
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe'
    })
    
    # Then try to login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data

def test_me_endpoint(client):
    """Test /me endpoint with authentication"""
    # Register and login to get token
    register_response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe'
    })
    
    token = register_response.get_json()['access_token']
    
    # Test /me endpoint
    response = client.get('/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['email'] == 'test@example.com' 