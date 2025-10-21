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
echo Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Set your bot token:
echo    set TELEGRAM_BOT_TOKEN=your_token_here
echo.
echo 2. Run the bot:
echo    python telebot.py
echo.
echo 3. In another terminal, run the API:
echo    python api_server.py
echo.
echo For deployment, see DEPLOYMENT.md
echo.
pause
