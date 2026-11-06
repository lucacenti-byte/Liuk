@echo off
setlocal
call "%~dp0_env.bat" || exit /b 1

net session >nul 2>&1
if errorlevel 1 (
  echo Esegui questo file come Amministratore.
  pause
  exit /b 1
)

if "%MODE%"=="exe" (
  "%APP%" --service stop
  "%APP%" --service remove
) else if "%MODE%"=="venv" (
  "%APP%" -m barcode_bridge --service stop
  "%APP%" -m barcode_bridge --service remove
) else (
  %APP% -m barcode_bridge --service stop
  %APP% -m barcode_bridge --service remove
)

echo Servizio rimosso.
pause
endlocal
