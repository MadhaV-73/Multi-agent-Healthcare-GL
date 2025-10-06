@echo off
echo ========================================
echo   Multi-Agent Healthcare Platform
echo   Starting Frontend and Backend
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Starting Backend API Server...
echo ========================================
start "Healthcare Backend API" cmd /k "cd /d %CD% && .venv\Scripts\python.exe api/main.py"

timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo Starting Frontend Streamlit App...
echo ========================================
start "Healthcare Frontend" cmd /k "cd /d %CD% && .venv\Scripts\python.exe -m streamlit run app.py"

echo.
echo ========================================
echo   Both servers are starting...
echo   Backend API: http://localhost:8000
echo   Frontend UI: http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit this window...
pause > nul
