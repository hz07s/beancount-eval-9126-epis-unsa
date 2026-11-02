@echo off
rem Doble clic: lanza setup.ps1 sin cambiar la politica de ejecucion del sistema.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
set "SETUP_EXIT=%ERRORLEVEL%"
rem Mantener la ventana abierta solo si se abrio con doble clic.
echo %CMDCMDLINE% | find /i "%~nx0" >nul && pause
exit /b %SETUP_EXIT%
