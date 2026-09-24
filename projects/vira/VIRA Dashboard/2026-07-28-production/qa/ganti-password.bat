@echo off
cd /d "%~dp0.."
python "qa\ganti-password.py" 2>nul
if errorlevel 9009 py "qa\ganti-password.py"
