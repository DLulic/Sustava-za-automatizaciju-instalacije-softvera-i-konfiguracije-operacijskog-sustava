@echo off

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -WorkingDirectory '%~dp0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

echo Updating python modules...

start /b /wait cmd.exe /c "pip install ttkbootstrap"
start /b /wait cmd.exe /c "pip install mysql.connector"

start /b /wait cmd.exe /c "python ./main.py"
