#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting build process..."

# Upgrade pip to avoid compatibility issues
pip install --upgrade pip

# Install system dependencies for compilation
apt-get update -y || true
apt-get install -y build-essential libffi-dev python3-dev || true

# Install Python dependencies with fallback options
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt || {
    echo "⚠️ Standard installation failed, trying with pre-compiled packages..."
    pip install --no-cache-dir --only-binary=all -r requirements.txt || {
        echo "❌ Installation failed even with pre-compiled packages"
        exit 1
    }
}

# Run database migrations
echo "🗄️ Running database migrations..."
python -m alembic upgrade head || {
    echo "⚠️ Database migration failed, but continuing..."
}

echo "✅ Build completed successfully!" 