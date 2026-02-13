@echo off
REM EasyCut Application Launcher Script for Windows
REM Professional YouTube Downloader and Audio Converter
REM Author: Deko Costa
REM Repository: https://github.com/dekouninter/EasyCut

echo.
echo =================================
echo   EasyCut - YouTube Downloader
echo =================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [INFO] Checking dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Check FFmpeg installation
echo.
echo [INFO] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found!
    echo Please install FFmpeg to enable audio conversion
    echo.
    echo Installation options:
    echo 1. Chocolatey: choco install ffmpeg
    echo 2. Winget: winget install FFmpeg
    echo 3. Manually: https://ffmpeg.org/download.html
    echo.
    echo Application can continue without FFmpeg, but audio conversion will not work
    echo.
) else (
    echo [OK] FFmpeg found
)

REM Launch application
echo.
echo [INFO] Launching EasyCut...
echo.
cd src
python easycut.py

REM Deactivate virtual environment on exit
deactivate

pause
