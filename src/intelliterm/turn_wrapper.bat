@echo off
:: IntelliTerm Wrapper for Windows CMD
:: This allows persistent CD changes that affect the parent shell.

:: Run the real IntelliTerm logic
iterm-internal %*

:: Check if a directory change was requested
set "HOOK_FILE=%USERPROFILE%\.intelliterm\last_cd"
if exist "%HOOK_FILE%" (
    for /f "usebackq delims=" %%i in ("%HOOK_FILE%") do (
        cd /d "%%i"
    )
    del "%HOOK_FILE%"
)
