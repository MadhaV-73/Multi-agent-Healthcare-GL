@echo off
echo ========================================
echo Multi-Agent Healthcare System Startup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

echo.
echo [2/4] Starting Backend API Server...
start "Healthcare API" cmd /k "python api\main.py"
timeout /t 3 /nobreak >nul

echo.
echo [3/4] Waiting for API to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [4/4] Starting Streamlit Frontend...
echo.
echo ========================================
echo    SYSTEM READY!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend UI:  http://localhost:8501
echo.
echo Press Ctrl+C in each window to stop
echo ========================================
echo.

REM Start Streamlit
streamlit run app_integrated.py

pause
