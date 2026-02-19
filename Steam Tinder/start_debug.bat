@echo on
cd /d "%~dp0"

echo Starting Steam Library Manager (DEBUG MODE)
start "" http://localhost:5000

python app.py

echo Server exited.
pause
