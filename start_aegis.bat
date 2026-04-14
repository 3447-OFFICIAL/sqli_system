@echo off
title Aegis Sentinel Tactical Startup
color 0B

echo ===================================================
echo     🛡️ AEGIS SENTINEL INITIALIZATION v2 🛡️
echo ===================================================
echo.
echo [!] BOOTING LOCAL NEURAL HUB...
echo.

:: Check for Python Dependencies
if not exist "venv\Scripts\python.exe" (
    echo [WARNING] Python virtual environment [venv] not found.
    echo [ACTION] Please run 'python -m venv venv' and install requirements.
)

:: Check for Node Dependencies
if not exist "frontend\node_modules" (
    echo [WARNING] Frontend dependencies [node_modules] not found.
    echo [ACTION] Please run 'cd frontend' and 'npm install'.
)

echo [1/2] Launching FastAPI Backend...
start "Aegis API" cmd /k "uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Launching Deep Dark UI...
cd frontend
start "Aegis UI" cmd /k "npm run dev"
cd ..

echo.
echo [SUCCESS] Tactical Stack Active.
echo Dashboard: http://localhost:5173
echo API Docs:  http://localhost:8000/docs
echo.
echo ===================================================
echo   Aegis Sentinel Neural Engine Operational.
echo ===================================================
echo.
pause
