@echo off
echo.
echo ========================================
echo   Reddit Meme Scraper - Quick Install
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install requirements
echo 📦 Installing Python packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install packages
    pause
    exit /b 1
)

echo ✅ Packages installed successfully
echo.

REM Run setup
echo 🚀 Starting interactive setup...
python setup.py

echo.
echo 🎉 Installation complete!
echo.
echo To start the meme scraper, run:
echo     python main.py
echo.
pause 