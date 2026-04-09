@echo off
title Aegis Sentinel Startup Sequence
color 0A

echo ===================================================
echo     🛡️ AEGIS SENTINEL INITIALIZATION 🛡️
echo ===================================================
echo.
echo [1/2] Booting FastAPI Backend API and ML Engine...
start "Aegis Backend (FastAPI)" cmd /k "uvicorn api.main:app --host 0.0.0.0 --port 8000"

echo     - Waiting for ML models to load into memory...
timeout /t 5 /nobreak > NUL

echo.
echo [2/2] Launching CSOC Streamlit Dashboard...
start "Aegis Dashboard (Streamlit)" cmd /k "streamlit run ui\app.py"

echo.
echo ===================================================
echo   System is now online! (Optimized for 127.0.0.1)
echo   Dashboard: http://localhost:8501
echo   Backend:   http://127.0.0.1:8000
echo ===================================================
echo.
pause
