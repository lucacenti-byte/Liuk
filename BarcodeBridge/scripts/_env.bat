@echo off
REM Imposta ROOT, PY e MODE (exe | venv | system)
set "ROOT=%~dp0.."
cd /d "%ROOT%"

set "MODE="
if exist "%ROOT%\BarcodeBridge.exe" (
  set "APP=%ROOT%\BarcodeBridge.exe"
  set "MODE=exe"
  goto :eof
)

if exist "%ROOT%\.venv\Scripts\python.exe" (
  set "APP=%ROOT%\.venv\Scripts\python.exe"
  set "MODE=venv"
  goto :eof
)

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set "APP=py -3"
  set "MODE=system"
  goto :eof
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  set "APP=python"
  set "MODE=system"
  goto :eof
)

echo [ERRORE] Python non trovato e manca BarcodeBridge.exe
echo Esegui prima scripts\installa_dipendenze.bat oppure scripts\build_standalone.bat
exit /b 1
