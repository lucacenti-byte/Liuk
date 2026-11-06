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
  "%APP%" --service stop
) else if "%MODE%"=="venv" (
  "%APP%" -m barcode_bridge --service stop
) else (
  %APP% -m barcode_bridge --service stop
)
echo Servizio fermato.
pause
endlocal
