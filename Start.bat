@echo off

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -WorkingDirectory '%~dp0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

echo Repairing WinGet package manager...

powershell -Command "Start-Process powershell -ArgumentList '-Command','Install-PackageProvider -Name NuGet -Force; Install-Module -Name Microsoft.WinGet.Client -Force; Repair-WinGetPackageManager -AllUsers' -Verb RunAs -Wait"

echo Updating python modules...

start /b /wait cmd.exe /c "winget install --id "Python.Python.3.13" --exact --source winget --accept-source-agreements --disable-interactivity --silent  --accept-package-agreements --force "

start /b /wait cmd.exe /c "pip install ttkbootstrap"
start /b /wait cmd.exe /c "pip install mysql.connector"

start /b /wait cmd.exe /c "python ./main.py"
