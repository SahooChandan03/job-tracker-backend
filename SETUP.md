# 🚀 Job Tracker Backend - Setup Guide

This guide will walk you through setting up and running the Job Tracker Backend project step by step.

## 📋 Prerequisites

Before starting, make sure you have the following installed:

- **Docker** and **Docker Compose** (for containerized setup)
- **Python 3.11+** (for local development)
- **Git** (to clone the repository)

## 🎯 Quick Start (Docker - Recommended)

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd job-tracker-backend
```

### Step 2: Set Up Environment Variables
```bash
# Copy the environment template
cp env.example .env

# Edit the .env file with your configuration
# The DATABASE_URL is already configured for Neon PostgreSQL
```

### Step 3: Start the Application
```bash
# Build and start all services
docker-compose up -d

# Check if services are running
docker-compose ps
```

### Step 4: Run Database Migrations
```bash
# Create and apply database migrations
docker-compose exec app python -m alembic upgrade head
```

### Step 5: Verify the Setup
```bash
# Check if the application is running
curl http://localhost:5000/graphql/health
```

You should see: `{"status": "healthy", "message": "Job Tracker API is running"}`

### Step 6: Access the Application
- **GraphQL Playground**: http://localhost:5000/graphql/playground
- **Health Check**: http://localhost:5000/graphql/health
- **API Endpoint**: http://localhost:5000/graphql

## 🔧 Local Development Setup

If you prefer to run the application locally without Docker:

### Step 1: Clone and Navigate
```bash
git clone <your-repository-url>
cd job-tracker-backend
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env file if needed
# The DATABASE_URL is already configured for Neon PostgreSQL
```

### Step 5: Initialize Database
```bash
# Initialize database tables
python run.py init-db

# Run migrations
python -m alembic upgrade head
```

### Step 6: Start Redis (Required)
```bash
# Install Redis if not already installed
# On macOS with Homebrew:
brew install redis
# On Ubuntu:
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Step 7: Run the Application
```bash
python run.py
```

The application will be available at http://localhost:5000

## 🧪 Testing the Setup

### Test Authentication
```bash
# Register a new user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Test GraphQL API
Visit http://localhost:5000/graphql/playground and try this query:

```graphql
query {
  me {
    id
    email
    firstName
    lastName
  }
}
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues
```bash
# Check if your Neon database is accessible
docker-compose exec app python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
try:
    engine.connect()
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

#### 2. Redis Connection Issues
```bash
# Check Redis connection
docker-compose exec app python -c "
import redis
import os
r = redis.from_url(os.getenv('REDIS_URL'))
try:
    r.ping()
    print('Redis connection successful!')
except Exception as e:
    print(f'Redis connection failed: {e}')
"
```

#### 3. Port Already in Use
```bash
# Check what's using port 5000
lsof -i :5000

# Kill the process or change the port in docker-compose.yml
```

#### 4. Docker Issues
```bash
# Restart Docker services
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs app
```

#### 5. Migration Issues
```bash
# Reset migrations (if needed)
docker-compose exec app python -m alembic downgrade base
docker-compose exec app python -m alembic upgrade head
```

## 📊 Running Tests

### Run All Tests
```bash
# With Docker
docker-compose exec app pytest tests/

# Locally
pytest tests/
```

### Run Specific Test Files
```bash
# Authentication tests
pytest tests/test_auth.py

# CRUD operation tests
pytest tests/test_crud.py
```

## 🗄️ Database Management

### Create New Migration
```bash
# With Docker
docker-compose exec app python run.py create-migration

# Locally
python run.py create-migration
```

### Apply Migrations
```bash
# With Docker
docker-compose exec app python run.py run-migrations

# Locally
python run.py run-migrations
```

### Check Migration Status
```bash
# With Docker
docker-compose exec app python -m alembic current

# Locally
python -m alembic current
```

## 🛠️ Development Commands

### Useful Docker Commands
```bash
# View logs
docker-compose logs -f app

# Access app container
docker-compose exec app bash

# Restart services
docker-compose restart

# Stop all services
docker-compose down
```

### Useful Local Commands
```bash
# Initialize database
python run.py init-db

# Create migration
python run.py create-migration

# Run migrations
python run.py run-migrations

# Run with debug mode
FLASK_DEBUG=1 python run.py
```

## 🚀 Production Deployment

### Environment Variables for Production
Make sure to update these in your `.env` file:

```bash
# Change these for production
JWT_SECRET_KEY=your-super-secure-production-key
SECRET_KEY=your-super-secure-flask-key
FLASK_ENV=production
FLASK_DEBUG=False
```

### Docker Production Build
```bash
# Build production image
docker build -t job-tracker-backend:prod .

# Run production container
docker run -p 5000:5000 \
  -e DATABASE_URL="your-production-db-url" \
  -e REDIS_URL="your-production-redis-url" \
  -e JWT_SECRET_KEY="your-production-jwt-key" \
  job-tracker-backend:prod
```

## 📱 API Usage Examples

### Authentication Flow
```bash
# 1. Register a user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# 2. Login to get token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# 3. Use token for authenticated requests
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "query { me { id email firstName lastName } }"
  }'
```

## ✅ Verification Checklist

- [ ] Docker containers are running (`docker-compose ps`)
- [ ] Database migrations applied successfully
- [ ] Health check endpoint returns success
- [ ] GraphQL Playground is accessible
- [ ] Can register a new user
- [ ] Can login and get JWT token
- [ ] Can make authenticated GraphQL queries
- [ ] Tests are passing

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: `docker-compose logs app`
2. **Verify environment**: Ensure `.env` file is properly configured
3. **Test database connection**: Use the troubleshooting commands above
4. **Check the README**: For detailed API documentation
5. **Review the GraphQL Playground**: For interactive API testing

## 🎉 Success!

Once you've completed all steps, you should have a fully functional Job Tracker Backend running with:

- ✅ Flask GraphQL API
- ✅ JWT Authentication
- ✅ PostgreSQL Database (Neon)
- ✅ Redis for OTP management
- ✅ Docker containerization
- ✅ Database migrations
- ✅ Test suite
- ✅ GraphQL Playground for testing

You can now start building your frontend application or use the API directly! 