@echo off
setlocal
cd /d "%~dp0.."

echo === Build pacchetto standalone (PyInstaller) ===
echo Eseguire su un PC Windows con Python 3.10+.
echo.

if not exist ".venv\Scripts\python.exe" (
  call "%~dp0installa_dipendenze.bat"
)

".venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 (
  echo Errore dipendenze build.
  pause
  exit /b 1
)

if exist "build\pyinstaller" rmdir /s /q "build\pyinstaller"
if exist "dist\BarcodeBridge" rmdir /s /q "dist\BarcodeBridge"

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean ^
  --name BarcodeBridge ^
  --onedir ^
  --console ^
  --distpath dist ^
  --workpath build\pyinstaller ^
  --specpath build ^
  --add-data "config.json;." ^
  run_barcode_bridge.py

if errorlevel 1 (
  echo Build fallita.
  pause
  exit /b 1
)

copy /Y "config.json" "dist\BarcodeBridge\config.json" >nul
xcopy /E /I /Y "scripts" "dist\BarcodeBridge\scripts" >nul
copy /Y "avvia.bat" "dist\BarcodeBridge\avvia.bat" >nul
copy /Y "README.md" "dist\BarcodeBridge\README.md" >nul

echo.
echo OK. Pacchetto pronto in:
echo   dist\BarcodeBridge\
echo Copia tutta quella cartella sui PC destinazione (nessun Python richiesto).
echo.
pause
endlocal
