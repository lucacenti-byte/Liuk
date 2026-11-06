@echo off
setlocal
cd /d "%~dp0.."

echo === BarcodeBridge: installazione dipendenze locali (.venv) ===

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PYLAUNCHER=py -3"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Installa Python 3.10+ da https://www.python.org/downloads/
    echo Durante l'installazione attiva "Add python.exe to PATH".
    pause
    exit /b 1
  )
  set "PYLAUNCHER=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo Creo ambiente virtuale .venv ...
  %PYLAUNCHER% -m venv .venv
  if errorlevel 1 (
    echo Errore creazione venv.
    pause
    exit /b 1
  )
)

echo Aggiorno pip e installo requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Errore installazione pacchetti.
  pause
  exit /b 1
)

echo.
echo OK. Dipendenze in .venv — la cartella e' autosufficiente su questo PC.
echo Avvio: avvia.bat   oppure   scripts\avvia_console.bat
echo.
pause
endlocal
