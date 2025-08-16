#!/bin/bash

# Japanese Learning App Setup Script

echo "🎌 Japanese Learning App - First Time Setup"
echo "==========================================="

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ All prerequisites found!"
echo ""

# Setup backend
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📥 Installing Python dependencies..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install --upgrade pip
pip install -r requirements.txt

cd ..

# Setup frontend
echo "📱 Setting up frontend..."
cd frontend

# Install npm dependencies
echo "📥 Installing Node.js dependencies..."
npm install

cd ..

# Setup Docker environment
echo "🐳 Setting up Docker environment..."
docker-compose pull postgres redis

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "  1. Run './dev-start.sh' to start the development environment"
echo "  2. Visit http://localhost:8000/docs to see the API documentation"
echo "  3. Use the Expo app on your phone to test the mobile app"
echo ""
echo "📚 For more information, check README.md"