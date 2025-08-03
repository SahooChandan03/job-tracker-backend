import pytest
from app import create_app
from app.config.database import db
from app.models import User, Job, Note
from datetime import date, datetime

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
def auth_token(client):
    """Create a user and return auth token"""
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe'
    })
    return response.get_json()['access_token']

def test_create_job(client, auth_token):
    """Test creating a job via GraphQL"""
    query = """
    mutation {
        createJob(jobData: {
            companyName: "Test Company"
            position: "Software Engineer"
            status: "applied"
            appliedOn: "2024-01-15"
        }) {
            success
            message
            job {
                id
                companyName
                position
                status
            }
        }
    }
    """
    
    response = client.post('/graphql', 
                          json={'query': query},
                          headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['createJob']['success'] == True

def test_get_jobs(client, auth_token):
    """Test getting all jobs via GraphQL"""
    # First create a job
    create_query = """
    mutation {
        createJob(jobData: {
            companyName: "Test Company"
            position: "Software Engineer"
            status: "applied"
            appliedOn: "2024-01-15"
        }) {
            success
        }
    }
    """
    client.post('/graphql', 
                json={'query': create_query},
                headers={'Authorization': f'Bearer {auth_token}'})
    
    # Then get all jobs
    query = """
    query {
        jobs {
            id
            companyName
            position
            status
        }
    }
    """
    
    response = client.post('/graphql', 
                          json={'query': query},
                          headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']['jobs']) > 0

def test_create_note(client, auth_token):
    """Test creating a note via GraphQL"""
    # First create a job
    create_job_query = """
    mutation {
        createJob(jobData: {
            companyName: "Test Company"
            position: "Software Engineer"
            status: "applied"
            appliedOn: "2024-01-15"
        }) {
            job {
                id
            }
        }
    }
    """
    job_response = client.post('/graphql', 
                              json={'query': create_job_query},
                              headers={'Authorization': f'Bearer {auth_token}'})
    job_id = job_response.get_json()['data']['createJob']['job']['id']
    
    # Then create a note
    query = """
    mutation {
        createNote(noteData: {
            jobId: "%s"
            content: "Test note content"
        }) {
            success
            message
            note {
                id
                content
            }
        }
    }
    """ % job_id
    
    response = client.post('/graphql', 
                          json={'query': query},
                          headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['createNote']['success'] == True 