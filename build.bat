@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM Decopro Windows Build
REM ============================================================

cd /d "%~dp0"

set APP_NAME=Decopro
set PROJECT_ROOT=%CD%
set ICON=%PROJECT_ROOT%\assets\decopro.ico
set PNG_ICON=%PROJECT_ROOT%\assets\decopro.png
set EXECUTABLE=%PROJECT_ROOT%\dist\%APP_NAME%\%APP_NAME%.exe

echo ========================================
echo Building %APP_NAME%
echo ========================================

REM ------------------------------------------------------------
REM Check icon exists
REM ------------------------------------------------------------

if not exist "%ICON%" (
    echo ERROR: Icon not found:
    echo %ICON%
    exit /b 1
)

REM ------------------------------------------------------------
REM Activate Conda environment
REM ------------------------------------------------------------

echo.
echo Activating Conda environment...

call conda activate decopro_env

if errorlevel 1 (
    echo ERROR: Could not activate Conda environment.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Set Python path
REM ------------------------------------------------------------

set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%

REM ------------------------------------------------------------
REM Clean previous build
REM ------------------------------------------------------------

echo.
echo Cleaning previous build...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM ------------------------------------------------------------
REM Build with PyInstaller
REM ------------------------------------------------------------

echo.
echo Building executable...

pyinstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "%APP_NAME%" ^
    --icon "%ICON%" ^
    --add-data "%PNG_ICON%;assets" ^
    gui\decopro_app.py

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM Check executable
REM ------------------------------------------------------------

if not exist "%EXECUTABLE%" (
    echo.
    echo ERROR: Executable was not created:
    echo %EXECUTABLE%
    pause
    exit /b 1
)

echo.
echo Build successful!

REM ------------------------------------------------------------
REM Copy PNG next to executable
REM ------------------------------------------------------------

copy /Y "%PNG_ICON%" "%PROJECT_ROOT%\dist\%APP_NAME%\decopro.png" > nul

REM ------------------------------------------------------------
REM Create a desktop shortcut
REM ------------------------------------------------------------

echo.
echo Creating desktop shortcut...

set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\%APP_NAME%.lnk

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; " ^
    "$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); " ^
    "$Shortcut.TargetPath = '%EXECUTABLE%'; " ^
    "$Shortcut.WorkingDirectory = '%PROJECT_ROOT%\dist\%APP_NAME%'; " ^
    "$Shortcut.IconLocation = '%ICON%,0'; " ^
    "$Shortcut.Description = 'Decopro Application'; " ^
    "$Shortcut.Save()"

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo Executable:
echo   %EXECUTABLE%
echo.
echo Desktop shortcut:
echo   %SHORTCUT%
echo.

pause
