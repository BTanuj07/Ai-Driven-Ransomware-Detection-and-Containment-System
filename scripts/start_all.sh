#!/bin/bash

echo "🚀 Starting ARCS System..."

# Start Docker containers
echo "📦 Starting Docker containers..."
docker-compose up -d

echo "⏳ Waiting for Kafka to initialize (30 seconds)..."
sleep 30

# Start backend in background
echo "🔧 Starting backend..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend in background
echo "🎨 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Start endpoint agent
echo "📡 Starting endpoint agent..."
cd endpoint_agent
python agent.py &
AGENT_PID=$!
cd ..

echo ""
echo "✅ ARCS System Started!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo ""
echo "Process IDs:"
echo "  Backend: $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo "  Agent: $AGENT_PID"
echo ""
echo "To stop all services, run: ./scripts/stop_all.sh"
