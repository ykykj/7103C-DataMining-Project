@echo off
echo ========================================
echo   Personal Assistant Agent - Starting
echo ========================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please create .env file with your API keys.
    pause
    exit /b 1
)

REM Run the application
python src\Main.py

pause

