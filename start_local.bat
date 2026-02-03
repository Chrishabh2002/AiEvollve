@echo off
echo Starting AiEvollve World...

REM Start Backend in a new window
start "AiEvollve Brain" cmd /k "python -m backend.app.main"

REM Wait for backend to initialize
timeout /t 5

REM Start Frontend in a new window
cd frontend
start "AiEvollve UI" cmd /k "npm run dev"

echo World is alive! 
echo Access UI at: http://localhost:3000
pause
