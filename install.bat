@echo off
REM ACCOTECH AI - One-click installer (just double-click this file)
REM Elevates to admin and runs install.ps1 with ExecutionPolicy bypass.

setlocal
cd /d "%~dp0"

REM ----- Self-elevate if not running as administrator -----
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c \"%~f0\"'"
    exit /b
)

echo.
echo   =====================================================
echo     ACCOTECH AI - Tally Automation System installer
echo   =====================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"

if %errorLevel% neq 0 (
    echo.
    echo Installation failed. See messages above.
    pause
    exit /b %errorLevel%
)

echo.
echo Done. You can now launch Accotech AI from your Desktop.
pause
