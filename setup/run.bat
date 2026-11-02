@echo off
rem Ejecuta un comando dentro del venv de una version.
rem Ejemplo: run.bat 3.2.3 bean-check archivo.beancount
setlocal
set "VENV="
if "%~1"=="3.2.3" set "VENV=%~dp0.venv-323"
if "%~1"=="2.3.6" set "VENV=%~dp0.venv-236"
if not defined VENV (
    echo Uso: run.bat {3.2.3^|2.3.6} comando [argumentos...] 1>&2
    exit /b 2
)
if not exist "%VENV%\Scripts\python.exe" (
    echo No existe %VENV%. Ejecuta primero setup.bat 1>&2
    exit /b 1
)
if "%~2"=="" (
    echo Uso: run.bat {3.2.3^|2.3.6} comando [argumentos...] 1>&2
    exit /b 2
)
set "VIRTUAL_ENV=%VENV%"
set "PYTHONUTF8=1"
set "PATH=%VENV%\Scripts;%PATH%"
rem Quita el primer argumento conservando comillas y parentesis del resto.
set "RUN_ALL=%*"
call set "RUN_CMD=%%RUN_ALL:*%~1 =%%"
%RUN_CMD%
exit /b %ERRORLEVEL%
