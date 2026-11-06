@echo off
setlocal
schtasks /Delete /TN "BarcodeBridge" /F
echo Attivita' BarcodeBridge rimossa (se esisteva).
pause
endlocal
