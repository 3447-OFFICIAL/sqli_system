@echo off
title Aegis Sentinel Tactical Command
color 0A

echo ===================================================
echo     🛡️  AEGIS SENTINEL TACTICAL BOOTSTRAP  🛡️
echo ===================================================
echo.
echo [!] INITIALIZING SYSTEM CORE...
echo.

:: Check for Virtual Environment
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .\venv
    echo [ACTION] Please run: python -m venv venv
    echo [ACTION] Then run: .\venv\Scripts\pip install -r requirements.txt
    pause
    exit /b
)

:: Launch FastAPI Backend
echo [1/2] Deploying Backend API Gateway (Port 8000)...
start "Aegis API" cmd /k ".\venv\Scripts\python.exe -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"

:: Check for Node Modules in Frontend
if not exist "frontend-simple\node_modules" (
    echo [!] WARNING: Node modules missing in frontend. Attempting npm install...
    cd frontend-simple
    call npm install
    cd ..
)

:: Launch Frontend Dashboard
echo [2/2] Launching Deep Dark 2.0 SOC Dashboard...
cd frontend-simple
start "Aegis SOC Dashboard" cmd /k "npm run dev"
cd ..

echo.
echo [SUCCESS] Tactical Stack Operational.
echo.
echo 🌐 Dashboard: http://localhost:5173
echo 📑 API Docs:  http://localhost:8000/docs
echo.
echo ===================================================
echo   AEGIS SENTINEL IS ACTIVE AND MONITORING TRAFFIC.
echo ===================================================
echo.
pause
