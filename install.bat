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

echo [1/3] Installing IntelliTerm package...
pip install .
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed. Check the output above.
    pause
    exit /b 1
)

echo.
echo [2/3] Setting up shell wrapper (for persistent CD support)...
for /f "delims=" %%i in ('python -c "import sysconfig; print(sysconfig.get_path('scripts'))"') do set "SCRIPTS_DIR=%%i"

if not exist "%SCRIPTS_DIR%" (
    echo ERROR: Could not find Python scripts directory.
    pause
    exit /b 1
)

copy /y "src\intelliterm\turn_wrapper.bat" "%SCRIPTS_DIR%\turn.bat" >nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to create turn.bat wrapper in %SCRIPTS_DIR%.
    pause
    exit /b 1
)

echo.
echo [3/3] Checking PATH...
powershell -Command "$p = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($p -notlike '*%SCRIPTS_DIR%*') { [Environment]::SetEnvironmentVariable('Path', $p + ';%SCRIPTS_DIR%', 'User'); Write-Host 'Added %SCRIPTS_DIR% to user PATH.' -ForegroundColor Cyan } else { Write-Host 'PATH is already correctly configured.' }"

echo.
echo ============================================
echo  IntelliTerm Setup Complete!
echo ============================================
echo.
echo IMPORTANT: If this is your first install, please RESTART
echo your terminal (CMD or PowerShell) to activate the 'turn' command.
echo.
echo Next steps:
echo   1. Run:  turn config set-key YOUR_API_KEY
echo   2. Try:  turn list all files
echo.
pause
