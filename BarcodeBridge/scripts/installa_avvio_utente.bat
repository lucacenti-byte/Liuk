@echo off
setlocal EnableDelayedExpansion
call "%~dp0_env.bat" || exit /b 1

echo === Avvio automatico all'accesso utente (consigliato) ===
echo Crea un'attivita' Pianificata che lancia BarcodeBridge in console
echo nella sessione desktop — necessaria per l'hook tastiera.
echo.

set "TASK=BarcodeBridge"

if "%MODE%"=="exe" (
  set "TR=\"%APP%\" --console"
) else if "%MODE%"=="venv" (
  set "TR=\"%APP%\" -m barcode_bridge --console"
) else (
  for /f "delims=" %%i in ('where python 2^>nul') do (
    set "TR=\"%%i\" -m barcode_bridge --console"
    goto :create
  )
  echo Usa installa_dipendenze.bat oppure build_standalone.bat prima.
  pause
  exit /b 1
)

:create
schtasks /Create /TN "%TASK%" /TR "!TR!" /SC ONLOGON /RL HIGHEST /F
if errorlevel 1 (
  echo Errore creazione attivita'. Prova come Amministratore.
  pause
  exit /b 1
)

echo.
echo Attivita' "%TASK%" creata (all'accesso utente).
echo Per rimuoverla: scripts\rimuovi_avvio_utente.bat
pause
endlocal
