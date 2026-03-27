@echo off
echo ========================================
echo ALSTOM MOC Workflow System Setup
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [2/4] Creating virtual environment...
python -m venv venv

echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [4/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo To run the application:
echo 1. venv\Scripts\activate
echo 2. python app.py
echo.
echo Then open: http://localhost:5000
echo.
pause