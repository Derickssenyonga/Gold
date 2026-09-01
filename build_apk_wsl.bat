@echo off
REM Gold Scalper APK Builder for Windows
REM This script uses WSL2 to build the Android APK

echo.
echo ============================================
echo  Gold Scalper Android APK Builder
echo ============================================
echo.

REM Check if WSL is installed
wsl --list --quiet > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: WSL2 is not installed.
    echo.
    echo To install WSL2, run in PowerShell as Administrator:
    echo   wsl --install
    echo.
    echo After installation, set up Ubuntu with:
    echo   1. wsl --install -d Ubuntu-22.04
    echo   2. Follow the initial setup prompts
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo Setting up build environment in WSL...
echo.

REM Copy project to WSL
echo Copying project to WSL...
wsl bash -c "rm -rf ~/gold_mt5_scalper 2>/dev/null; mkdir -p ~"
wsl -- cp -r /mnt/c/Users/%USERNAME%/gold_mt5_scalper ~

REM Run the build
echo.
echo Building APK...
echo.
wsl bash -c "cd ~/gold_mt5_scalper/android_app && buildozer android debug"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed. See details above.
    pause
    exit /b 1
)

REM Copy APK back to Windows
echo.
echo Copying APK back to Windows...
wsl -- cp ~/gold_mt5_scalper/android_app/bin/goldscalper*.apk /mnt/c/Users/%USERNAME%/gold_mt5_scalper/android_app/bin/

echo.
echo ============================================
echo  APK Build Complete!
echo ============================================
echo.
echo APK Location:
echo   C:\Users\%USERNAME%\gold_mt5_scalper\android_app\bin\
echo.
echo Next steps:
echo   1. Transfer the APK to your Android device
echo   2. Enable "Install from unknown sources" in Settings
echo   3. Tap the APK file to install
echo.
pause
