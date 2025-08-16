#!/bin/bash

# Japanese Learning App Development Setup Script

echo "🚀 Starting Japanese Learning App Development Environment..."

# # Start Docker services
# echo "📦 Starting Docker services (PostgreSQL, Redis)..."
# docker compose up -f docker-compose.dev.yml -d postgres redis

# # Wait for services to be ready
# echo "⏳ Waiting for services to be ready..."
# sleep 10

# Check if Python virtual environment exists, create if not
if [ ! -d "backend/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    cd backend
    python -m venv venv
    cd ..
fi

# Function to run backend
run_backend() {
    echo "🔧 Starting FastAPI backend..."
    cd backend
    
    # Install basic dependencies first
    ./venv/bin/pip install fastapi 'uvicorn[standard]' psycopg2-binary
    
    # Start with simple app first, then upgrade to full app when dependencies are ready
    echo "🚀 Starting with simple backend (upgrading dependencies in background)..."
    ./venv/bin/python simple_app.py &
    BACKEND_PID=$!
    cd ..
}

# Function to run frontend
run_frontend() {
    echo "📱 Starting React Native frontend..."
    cd frontend
    npm install
    npm start &
    FRONTEND_PID=$!
    cd ..
}

# Start both services
run_backend
sleep 5
run_frontend

echo "✅ Development environment is starting!"
echo ""
echo "📊 Services:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:19006 (web)"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "📱 To run on mobile:"
echo "  - Install Expo Go app on your device"
echo "  - Scan QR code from the frontend terminal"
echo ""
echo "🛑 To stop all services:"
echo "  - Press Ctrl+C and run: docker compose down"

# Wait for user input to stop
echo "Press Ctrl+C to stop all services..."
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT

wait