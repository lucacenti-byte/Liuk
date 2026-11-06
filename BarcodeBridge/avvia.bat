@echo off
cd /d "%~dp0"

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set PY=py -3
) else (
  set PY=python
)

%PY% -c "import keyboard" 2>nul
if errorlevel 1 (
  echo Installazione dipendenze...
  %PY% -m pip install -r requirements.txt
)

echo.
echo Avvio BarcodeBridge...
echo Se la tastiera non viene intercettata, clic destro su questo file
echo e scegli "Esegui come amministratore".
echo.
%PY% barcode_bridge.py
pause
