@echo off
echo Stopping ARCS System...

echo Stopping Python processes...
taskkill /F /IM python.exe 2>nul

echo Stopping Node processes...
taskkill /F /IM node.exe 2>nul

echo Stopping Docker containers...
docker-compose down

echo ARCS System Stopped
pause
