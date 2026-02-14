@echo off
REM EasyCut Quick Start Script for Windows
REM Professional YouTube Downloader and Audio Converter
REM Author: Deko Costa
REM Repository: https://github.com/dekouninter/EasyCut

title EasyCut - YouTube Downloader
color 0A

echo.
echo ========================================
echo.
echo   Starting EasyCut Professional Application
echo.
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if exist venv (
    echo [OK] Virtual environment found
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% equ 0 (
        echo [OK] Virtual environment created
    ) else (
        echo [ERROR] Failed to create virtual environment
        echo Make sure Python 3.8+ is installed and added to PATH
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Checking dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Execute application
echo.
echo [INFO] Launching EasyCut...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application failed to start
    echo Please check the error message above
    pause
)

REM Deactivate virtual environment
deactivate
