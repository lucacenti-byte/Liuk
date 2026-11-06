@echo off
setlocal
call "%~dp0_env.bat" || exit /b 1

echo Avvio BarcodeBridge (console/batch). Ctrl+C per uscire.
if "%MODE%"=="exe" (
  "%APP%" --console
) else if "%MODE%"=="venv" (
  "%APP%" -m barcode_bridge --console
) else (
  %APP% -m barcode_bridge --console
)
endlocal
