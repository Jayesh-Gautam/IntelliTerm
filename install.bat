@echo off
echo ============================================
echo  IntelliTerm Installer
echo ============================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/2] Installing IntelliTerm...
pip install .
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed. Check the output above.
    pause
    exit /b 1
)

echo.
echo [2/2] Setup complete.
echo.
echo ============================================
echo  IntelliTerm has been installed.
echo ============================================
echo.
echo Next steps:
echo   1. Get a free API key from: https://console.groq.com/keys
echo   2. Run: turn config set-key YOUR_API_KEY
echo   3. Try:  turn list all files in this directory
echo   4. Or:   turn shell   (for interactive mode)
echo.
pause
