@echo off
REM Dagster Example Project - Setup Script for Windows
REM Run this script to set up the project and start Dagster

echo ================================
echo Dagster Example Project Setup
echo ================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo    [OK] Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -e "." >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo    [OK] Dependencies installed
echo.

REM Check installation
echo Verifying installation...
dagster --version
echo.

echo ================================
echo Setup complete!
echo ================================
echo.
echo Next steps:
echo.
echo 1. Start Dagster:
echo    venv\Scripts\activate
echo    dagster dev
echo.
echo 2. Open your browser to:
echo    http://localhost:3000
echo.
echo 3. Explore the assets and materialize them!
echo.

pause
