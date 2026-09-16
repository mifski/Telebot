@echo off
echo.
echo ========================================
echo YouTube to Telegram Bot - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Install requirements
echo Installing dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt

REM Create .env from the example if it doesn't exist yet
if not exist .env (
    copy .env.example .env >nul
    echo Created .env - open it and paste your bot token from @BotFather
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Put your bot token in .env  (TELEGRAM_BOT_TOKEN=...)
echo.
echo 2. Run the bot (this also starts the API for the extension):
echo    .venv\Scripts\python.exe telebot.py
echo.
echo 3. Want it running 24/7 without your computer on?
echo    See DEPLOYMENT.md - about 5 minutes on Railway.
echo.
pause
