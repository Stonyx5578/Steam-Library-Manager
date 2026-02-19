@echo on
echo ==================================================
echo Building Steam Library Manager EXE...
echo ==================================================

REM Step 1: Make sure we are in the project folder
cd /d "%~dp0"

REM Step 2: Upgrade pip and install PyInstaller (optional if not installed)
echo Installing PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller

REM Step 3: Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist app.spec del /f /q app.spec

REM Step 4: Build the EXE with templates and static folders
echo Running PyInstaller...
python -m PyInstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py

REM Step 5: Finished
echo ==================================================
echo Build complete! Your EXE is in the 'dist' folder.
echo ==================================================
pause
