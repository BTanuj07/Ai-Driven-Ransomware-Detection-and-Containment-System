@echo off
echo ========================================
echo    ARCS System Startup Script
echo ========================================
echo.

REM Start Backend
echo [1/2] Starting Backend Server...
echo      Location: backend/
echo      Port: 8000
start "ARCS Backend" cmd /k "cd backend && echo Starting ARCS Backend... && python main.py"
echo      Status: Backend terminal opened
echo      Wait for: 'Uvicorn running on http://0.0.0.0:8000'
echo.
timeout /t 8 /nobreak > nul

REM Start Frontend
echo [2/2] Starting Frontend Server...
echo      Location: frontend/
echo      Port: 3000
start "ARCS Frontend" cmd /k "cd frontend && echo Starting ARCS Frontend... && npm run dev"
echo      Status: Frontend terminal opened
echo      Wait for: 'Local: http://localhost:3000/'
echo.
timeout /t 5 /nobreak > nul

echo ========================================
echo    ARCS System Starting...
echo ========================================
echo.
echo IMPORTANT: Check both terminal windows!
echo.
echo Backend Terminal:
echo   - Should show: "Uvicorn running on http://0.0.0.0:8000"
echo   - If you see errors, fix them before proceeding
echo.
echo Frontend Terminal:
echo   - Should show: "Local: http://localhost:3000/"
echo   - If you see errors, fix them before proceeding
echo.
echo Once both are running:
echo   1. Open browser to: http://localhost:3000
echo   2. Login with your credentials
echo   3. Alerts should appear on dashboard
echo.
echo To verify everything is working:
echo   Run: powershell -ExecutionPolicy Bypass -File test_connection.ps1
echo.
echo ========================================
echo Press any key to open dashboard...
echo (Backend and Frontend will keep running)
echo ========================================
pause > nul

start http://localhost:3000

echo.
echo To stop ARCS, close both terminal windows
echo or press Ctrl+C in each window
