#!/bin/bash

# Bank Data Catalog - Quick Start Script
# This script helps you start the full stack application

set -e

echo "🏦 Bank Data Catalog - Full Stack Startup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with:"
    echo "  NEO4J_URI=bolt://localhost:7687"
    echo "  NEO4J_USER=neo4j"
    echo "  NEO4J_PASSWORD=your_password"
    echo "  OPENAI_API_KEY=your_openai_key"
    exit 1
fi

echo "✅ Environment file found"
echo ""

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check Neo4j
echo "🔍 Checking Neo4j..."
if check_port 7687; then
    echo "✅ Neo4j is running on port 7687"
else
    echo "❌ Neo4j is not running on port 7687"
    echo "Please start Neo4j before continuing"
    exit 1
fi
echo ""

# Backend setup
echo "🐍 Setting up Backend..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -q -r backend_requirements.txt

echo "✅ Backend setup complete"
echo ""

# Frontend setup
echo "⚛️  Setting up Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
else
    echo "✅ Frontend dependencies already installed"
fi

cd ..
echo ""

# Start backend
echo "🚀 Starting Backend API..."
source venv/bin/activate
python backend_api.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if check_port 8000; then
        echo "✅ Backend is ready on http://localhost:8000"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check backend.log for errors"
        exit 1
    fi
    sleep 1
done
echo ""

# Start frontend
echo "🚀 Starting Frontend..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
for i in {1..30}; do
    if check_port 5173; then
        echo "✅ Frontend is ready on http://localhost:5173"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start. Check frontend.log for errors"
        exit 1
    fi
    sleep 1
done

cd ..
echo ""
echo "=========================================="
echo "✅ All services are running!"
echo ""
echo "📱 Frontend:  http://localhost:5173"
echo "🔌 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop watching logs..."
echo ""

# Follow logs
tail -f backend.log frontend.log
