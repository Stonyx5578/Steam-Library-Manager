@echo off
cd /d "%~dp0"

echo Starting Steam Library Manager...
start "" http://localhost:5000
python app.py
