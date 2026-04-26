#!/bin/bash

echo "🛑 Stopping ARCS System..."

# Kill Python processes
echo "Stopping Python processes..."
pkill -f "python main.py"
pkill -f "python agent.py"

# Kill Node processes
echo "Stopping Node processes..."
pkill -f "vite"

# Stop Docker containers
echo "Stopping Docker containers..."
docker-compose down

echo "✅ ARCS System Stopped"
