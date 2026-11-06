@echo off
setlocal
call "%~dp0_env.bat" || exit /b 1

echo === Installazione servizio Windows BarcodeBridge ===
echo Richiede privilegi di Amministratore.
echo.
echo ATTENZIONE: l'hook tastiera funziona nella sessione desktop utente.
echo Se il servizio gira come LocalSystem puo' NON vedere i barcode.
echo In quel caso preferisci scripts\installa_avvio_utente.bat
echo.

net session >nul 2>&1
if errorlevel 1 (
  echo Esegui questo file come Amministratore.
  pause
  exit /b 1
)

if "%MODE%"=="exe" (
  "%APP%" --service install
  "%APP%" --service start
) else if "%MODE%"=="venv" (
  "%APP%" -m barcode_bridge --service install
  "%APP%" -m barcode_bridge --service start
) else (
  %APP% -m barcode_bridge --service install
  %APP% -m barcode_bridge --service start
)

echo.
echo Servizio installato. Log in: logs\barcode_bridge.log
pause
endlocal
