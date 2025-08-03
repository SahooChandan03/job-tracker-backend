# 🚀 Job Tracker Backend - Quick Start Summary

## ✅ **Project Successfully Set Up!**

Your Job Tracker Backend is now running locally and ready to use!

## 🎯 **How to Run the Project**

### **Option 1: Automated Setup (Recommended)**
```bash
./quick-start.sh
```

### **Option 2: Manual Setup**
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp env.example .env

# 4. Initialize database
FLASK_APP=app python -c "
from app import create_app
from app.database import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"

# 5. Start Redis (if not running)
brew services start redis  # macOS
# OR
sudo systemctl start redis-server  # Ubuntu

# 6. Run the application
FLASK_APP=app FLASK_RUN_PORT=8000 python -m flask run --host=0.0.0.0 --port=8000
```

## 🌐 **Access Points**

- **GraphQL Playground**: http://localhost:8000/graphql/playground
- **Health Check**: http://localhost:8000/graphql/health
- **API Endpoint**: http://localhost:8000/graphql

## 🧪 **Test the API**

### **Register a User**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### **Login**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### **GraphQL Query**
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "query { me { id email firstName lastName } }"}'
```

## 🛠️ **Useful Commands**

### **Stop the Application**
```bash
./stop-app.sh
```

### **View Logs**
The application logs are displayed in the terminal where you ran the quick-start script.

### **Restart the Application**
```bash
./stop-app.sh
./quick-start.sh
```

## 📊 **Features Working**

✅ **JWT Authentication** - Register, login, and token verification  
✅ **GraphQL API** - Queries and mutations for jobs and notes  
✅ **PostgreSQL Database** - Connected to your Neon database  
✅ **Redis** - OTP management and caching  
✅ **Health Check** - API status monitoring  
✅ **GraphQL Playground** - Interactive API testing  

## 🔧 **Configuration**

- **Database**: Neon PostgreSQL (configured in `.env`)
- **Port**: 8000 (to avoid conflicts with AirPlay on macOS)
- **Environment**: Development mode with debug enabled

## 🆘 **Troubleshooting**

### **Port Already in Use**
The application automatically uses port 8000 to avoid conflicts with AirPlay on macOS.

### **Database Connection Issues**
Check your Neon database connection string in the `.env` file.

### **Redis Not Running**
```bash
# macOS
brew services start redis

# Ubuntu
sudo systemctl start redis-server
```

### **Stop All Processes**
```bash
./stop-app.sh
```

## 🎉 **Success!**

Your Job Tracker Backend is now fully functional and ready for development!

- **API Documentation**: Visit http://localhost:8000/graphql/playground
- **Health Status**: http://localhost:8000/graphql/health
- **Full Documentation**: See `README.md` and `SETUP.md`

Happy coding! 🚀 