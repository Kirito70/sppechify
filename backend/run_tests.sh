#!/bin/bash

# Test Script for Japanese Learning API
# Run this script from the backend directory

echo "🧪 Running Japanese Learning API Tests..."
echo "======================================"

# Set environment variables
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=admin
export UPLOAD_PATH=./uploads
export PYTHONPATH=.

# Run tests
echo "📊 Running pytest tests..."
./venv/bin/pytest tests/ -v --tb=short

echo ""
echo "🔍 Running basic database connection test..."
./venv/bin/python ../test_basic_connection.py

echo ""
echo "✅ Test suite completed!"