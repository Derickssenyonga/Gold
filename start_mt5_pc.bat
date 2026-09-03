@echo off
setlocal
cd /d "%~dp0"

echo Gold Scalper MT5 PC launcher
if not exist ".env" (
    echo ERROR: .env is missing.
    echo Copy .env.example to .env and enter your MT5 demo credentials.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo ERROR: Python 3 was not found. Install Python 3.11 or newer.
        pause
        exit /b 1
    )
)

echo Installing or checking dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Dependency installation failed.
    pause
    exit /b 1
)

echo Starting MT5 bot. Press Ctrl+C to stop it.
.venv\Scripts\python.exe start_gold_bot.py

if errorlevel 1 (
    echo.
    echo The bot stopped with an error. Check MT5_PATH, MT5_SERVER, credentials, and SYMBOL in .env.
    pause
)
endlocal
