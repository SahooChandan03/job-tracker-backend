# Job Application Tracker Backend

A production-ready Flask API for tracking job applications, built with PostgreSQL, Redis, and JWT authentication. Features both REST and GraphQL APIs with unified OTP security system.

## 🚀 Features

- **Dual API Support**: REST and GraphQL APIs
- **JWT Authentication** with secure token-based auth
- **Unified OTP System** with module-based rate limiting
- **PostgreSQL Database** with SQLAlchemy ORM
- **Redis** for OTP management and caching
- **Alembic Migrations** for database schema management
- **Pydantic Schemas** for data validation
- **Service Layer Architecture** for clean separation of concerns
- **GraphQL Playground** for API testing

## 📁 Project Structure

```
job-tracker-backend/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── main.py                  # GraphQL schema and resolvers
│   ├── database.py              # SQLAlchemy configuration
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── job.py
│   │   └── note.py
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── job.py
│   │   └── note.py
│   ├── auth/                    # Authentication module
│   │   ├── __init__.py
│   │   ├── jwt.py
│   │   └── routes.py
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py      # User management + OTP logic
│   │   ├── job_service.py       # Job CRUD operations
│   │   └── note_service.py      # Note CRUD operations
│   └── routers/                 # API routes
│       ├── __init__.py
│       └── graphql_routes.py
├── alembic/                     # Database migrations
├── tests/                       # Test suite
├── requirements.txt             # Python dependencies
├── run.py                      # Application entry point
└── README.md                   # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL (local or cloud)
- Redis (local or cloud)

### Local Development Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd job-tracker-backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**

   ```bash
   cp env.example .env
   # Edit .env with your database and Redis URLs
   ```

5. **Initialize database:**

   ```bash
   python run.py init-db
   python -m alembic upgrade head
   ```

6. **Run the application:**

   ```bash
   python run.py
   ```

7. **Access the application:**

   - API: http://localhost:5000
   - GraphQL Playground: http://localhost:5000/graphql/playground

### Database Setup

#### Option 1: Local PostgreSQL

1. **Install PostgreSQL** on your system
2. **Create a database:**

   ```sql
   CREATE DATABASE job_tracker;
   ```

3. **Update .env file:**

   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/job_tracker
   ```

#### Option 2: Cloud PostgreSQL (Recommended)

1. **Use a cloud provider** like Neon, Supabase, or Railway
2. **Get your connection string** from the provider
3. **Update .env file** with the connection string

### Redis Setup

#### Option 1: Local Redis

1. **Install Redis** on your system
2. **Start Redis server:**

   ```bash
   redis-server
   ```

3. **Update .env file:**

   ```
   REDIS_URL=redis://localhost:6379/0
   ```

#### Option 2: Cloud Redis

1. **Use a cloud provider** like Redis Cloud, Upstash, or Railway
2. **Get your connection string** from the provider
3. **Update .env file** with the connection string

## 🔐 Authentication & OTP System

### Unified OTP Security Features

- **Module-based rate limiting**: 3 attempts per module per 24 hours
- **Wrong OTP protection**: 5 wrong attempts → 30-minute block
- **Unified blocking**: OTP requests and resend attempts counted together
- **Auto-reset**: All counters reset on successful verification

### Register User

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "message": "OTP sent successfully",
  "attempts_remaining": 2
}
```

### Verify OTP

```bash
curl -X POST http://localhost:5000/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456"
  }'
```

### Resend OTP

```bash
curl -X POST http://localhost:5000/auth/resend-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "module": "register"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "message": "Login OTP sent successfully",
  "attempts_remaining": 2
}
```

**Then verify the OTP:**
```bash
curl -X POST http://localhost:5000/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456",
    "module": "login"
  }'
```

### Forget Password

```bash
# Send password reset OTP
curl -X POST http://localhost:5000/auth/forget-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'

# Reset password with OTP
curl -X POST http://localhost:5000/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "code": "123456",
    "new_password": "newpassword123"
  }'
```

### Get User Profile

```bash
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 GraphQL API

### Queries

#### Get All Jobs

```graphql
query {
  jobs {
    id
    companyName
    position
    status
    appliedOn
    createdAt
  }
}
```

#### Get Job by ID

```graphql
query {
  job(id: "job-uuid") {
    id
    companyName
    position
    status
    appliedOn
    createdAt
  }
}
```

#### Get Notes for Job

```graphql
query {
  jobNotes(jobId: "job-uuid") {
    id
    content
    reminderTime
    createdAt
  }
}
```

#### Get Current User

```graphql
query {
  me {
    id
    email
    firstName
    lastName
    isActive
  }
}
```

### Mutations

#### Create Job

```graphql
mutation {
  createJob(jobData: {
    companyName: "Google"
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
    }
  }
}
```

#### Update Job

```graphql
mutation {
  updateJob(id: "job-uuid", jobData: {
    status: "interviewing"
  }) {
    success
    message
    job {
      id
      status
    }
  }
}
```

#### Delete Job

```graphql
mutation {
  deleteJob(id: "job-uuid") {
    success
    message
  }
}
```

#### Create Note

```graphql
mutation {
  createNote(noteData: {
    jobId: "job-uuid"
    content: "Follow up with recruiter next week"
    reminderTime: "2024-01-20T10:00:00Z"
  }) {
    success
    message
    note {
      id
      content
    }
  }
}
```

#### Delete Note

```graphql
mutation {
  deleteNote(id: "note-uuid") {
    success
    message
  }
}
```

## 🔒 Security Features

### OTP Rate Limiting

| Module | Limit | Block Duration | Window |
|--------|-------|----------------|---------|
| `register` | 3 attempts | 20 minutes | 24 hours |
| `login` | 3 attempts | 24 hours | 24 hours |
| `forgetpassword` | 3 attempts | 24 hours | 24 hours |

### Wrong OTP Protection

- **5 wrong attempts** within 1 hour → **30-minute block**
- **Module-specific tracking** for each OTP type
- **Auto-reset** on successful verification

### Redis Key Structure

```
otp:{module}:{email}                    # OTP storage
wrong_otp_attempts:{email}:{module}     # Wrong attempt tracking
blocked_user:{module}:{email}           # Unified blocking
otp_limit:{module}:{email}              # Request limit tracking
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run specific test files:

```bash
pytest tests/test_auth.py
pytest tests/test_crud.py
```

## 🗄️ Database Migrations

### Create Migration

```bash
python run.py create-migration
```

### Run Migrations

```bash
python run.py run-migrations
```

## 🔧 Configuration

### Environment Variables

| Variable                            | Description                  | Default                                              |
| ----------------------------------- | ---------------------------- | ---------------------------------------------------- |
| `DATABASE_URL`                    | PostgreSQL connection string | db connection url                                    |
| `REDIS_URL`                       | Redis connection string      | `redis://localhost:6379/0`                         |
| `JWT_SECRET_KEY`                  | JWT signing key              | `your-super-secret-jwt-key-change-in-production`   |
| `JWT_ALGORITHM`                   | JWT algorithm                | `HS256`                                            |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time            | `30`                                               |
| `SECRET_KEY`                      | Flask secret key             | `your-super-secret-flask-key-change-in-production` |
| `OTP_EXPIRY_SECONDS`              | OTP expiry time              | `300`                                              |

## 📋 API Endpoints

### REST Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/verify-otp` - Verify registration OTP
- `POST /auth/resend-otp` - Resend OTP for any module
- `POST /auth/login` - User login with password
- `POST /auth/forget-password` - Send password reset OTP
- `POST /auth/reset-password` - Reset password with OTP
- `GET /auth/me` - Get current user profile

### GraphQL Endpoints

- `POST /graphql` - GraphQL API endpoint
- `GET /graphql/playground` - GraphQL Playground UI

## 🏗️ Architecture

### Service Layer

- **UserService**: Handles user registration, authentication, and OTP management
- **JobService**: Manages job CRUD operations
- **NoteService**: Manages note CRUD operations

### Clean Separation

- **Routes**: Handle HTTP requests/responses only
- **Services**: Contain all business logic
- **Models**: Define data structure
- **Schemas**: Handle validation

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Update all secret keys in production
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service
4. **HTTPS**: Enable SSL/TLS
5. **CORS**: Configure CORS for your frontend domain
6. **Rate Limiting**: Implement rate limiting
7. **Logging**: Configure proper logging
8. **Monitoring**: Add health checks and monitoring

### Deployment Options

#### Option 1: Traditional Server

1. **Set up a server** (Ubuntu, CentOS, etc.)
2. **Install Python, PostgreSQL, and Redis**
3. **Clone the repository**
4. **Set up environment variables**
5. **Run with Gunicorn:**

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

#### Option 2: Cloud Platforms

- **Heroku**: Deploy with Procfile
- **Railway**: Connect GitHub repository
- **Render**: Deploy from Git repository
- **DigitalOcean App Platform**: Deploy with managed services

#### Option 3: Container Platforms

- **Google Cloud Run**: Serverless container deployment
- **AWS ECS**: Container orchestration
- **Azure Container Instances**: Managed container service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the GraphQL Playground for API documentation
- Review the test files for usage examples
