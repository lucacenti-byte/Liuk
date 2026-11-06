@echo off
setlocal
call "%~dp0_env.bat" || exit /b 1
net session >nul 2>&1
if errorlevel 1 (
  echo Esegui come Amministratore.
  pause
  exit /b 1
)
if "%MODE%"=="exe" (
  "%APP%" --service start
) else if "%MODE%"=="venv" (
  "%APP%" -m barcode_bridge --service start
) else (
  %APP% -m barcode_bridge --service start
)
echo Servizio avviato.
pause
endlocal
