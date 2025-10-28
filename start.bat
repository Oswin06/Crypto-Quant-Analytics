@echo off
echo ============================================================
echo Quant Analytics Dashboard - Starting
echo ============================================================
echo.

echo [1/2] Starting Backend API...
start cmd /k "uvicorn src.backend.api:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Streamlit Frontend...
start cmd /k "streamlit run src/frontend/app.py --server.port 8501"

echo.
echo ============================================================
echo Dashboard will open at http://localhost:8501
echo API will be at http://localhost:8000
echo ============================================================
echo.
echo Press any key to exit...
pause >nul

