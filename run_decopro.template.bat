@echo off
setlocal

REM Go to the project root (where this .bat file is located)
cd /d "%~dp0"

REM Activate the Conda environment
call conda activate decopro_env

REM Make the project root available for Python imports
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Run the application
python gui\decopro_app.py

pause