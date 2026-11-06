@echo off
setlocal
call "%~dp0_env.bat" || exit /b 1

echo Avvio BarcodeBridge (GUI)...
if "%MODE%"=="exe" (
  "%APP%"
) else if "%MODE%"=="venv" (
  "%APP%" -m barcode_bridge
) else (
  %APP% -m barcode_bridge
)
endlocal
