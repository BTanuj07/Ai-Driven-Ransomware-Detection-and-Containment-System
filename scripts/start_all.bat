@echo off
echo Starting ARCS System...

echo Starting Docker containers...
docker-compose up -d

echo Waiting for Kafka to initialize (30 seconds)...
timeout /t 30 /nobreak

echo Starting backend...
start cmd /k "cd backend && python main.py"

timeout /t 5 /nobreak

echo Starting frontend...
start cmd /k "cd frontend && npm run dev"

echo Starting endpoint agent...
start cmd /k "cd endpoint_agent && python agent.py"

echo.
echo ARCS System Started!
echo.
echo Dashboard: http://localhost:3000
echo Backend API: http://localhost:8000
echo.
echo Press any key to exit this window...
pause
