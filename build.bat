@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM Decopro Windows Build
REM ============================================================

REM ------------------------------------------------------------
REM Always run from the directory containing this BAT file
REM ------------------------------------------------------------

cd /d "%~dp0"

set "APP_NAME=Decopro"
set "PROJECT_ROOT=%CD%"

set "ICON=%PROJECT_ROOT%\assets\decopro.ico"
set "PNG_ICON=%PROJECT_ROOT%\assets\decopro.png"
set "ENV_FILE=%PROJECT_ROOT%\environment.yml"

set "ENV_NAME=decopro_env"

set "DIST_DIR=%PROJECT_ROOT%\dist\%APP_NAME%"
set "EXECUTABLE=%DIST_DIR%\%APP_NAME%.exe"

REM ------------------------------------------------------------
REM Miniconda configuration
REM ------------------------------------------------------------

set "CONDA_ROOT=%USERPROFILE%\miniconda3"
set "CONDA_EXE=%CONDA_ROOT%\Scripts\conda.exe"

set "MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set "MINICONDA_INSTALLER=%TEMP%\Miniconda3-latest-Windows-x86_64.exe"


echo.
echo ========================================
echo        %APP_NAME% Windows Build
echo ========================================
echo.


REM ============================================================
REM Check required project files
REM ============================================================

echo Checking project files...
echo.

if not exist "%ICON%" (
    echo ERROR: Icon not found:
    echo   %ICON%
    goto BUILD_FAILED
)

if not exist "%PNG_ICON%" (
    echo ERROR: PNG icon not found:
    echo   %PNG_ICON%
    goto BUILD_FAILED
)

if not exist "%ENV_FILE%" (
    echo ERROR: environment.yml not found:
    echo   %ENV_FILE%
    goto BUILD_FAILED
)

echo Project files OK.


REM ============================================================
REM Locate Conda
REM
REM IMPORTANT:
REM Only conda.exe is used.
REM We NEVER call:
REM   conda
REM   conda.bat
REM   activate
REM   conda shell.bat hook
REM
REM This prevents BAT recursion.
REM ============================================================

echo.
echo ========================================
echo Checking for Conda
echo ========================================
echo.


REM ------------------------------------------------------------
REM 1. User Miniconda
REM ------------------------------------------------------------

if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    set "CONDA_ROOT=%USERPROFILE%\miniconda3"
    set "CONDA_EXE=%USERPROFILE%\miniconda3\Scripts\conda.exe"
    echo Found Miniconda:
    echo   %CONDA_ROOT%
    goto CONDA_READY
)


REM ------------------------------------------------------------
REM 2. User Anaconda
REM ------------------------------------------------------------

if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    set "CONDA_ROOT=%USERPROFILE%\anaconda3"
    set "CONDA_EXE=%USERPROFILE%\anaconda3\Scripts\conda.exe"
    echo Found Anaconda:
    echo   %CONDA_ROOT%
    goto CONDA_READY
)


REM ------------------------------------------------------------
REM 3. System Miniconda
REM ------------------------------------------------------------

if exist "%ProgramData%\miniconda3\Scripts\conda.exe" (
    set "CONDA_ROOT=%ProgramData%\miniconda3"
    set "CONDA_EXE=%ProgramData%\miniconda3\Scripts\conda.exe"
    echo Found system Miniconda:
    echo   %CONDA_ROOT%
    goto CONDA_READY
)


REM ------------------------------------------------------------
REM 4. System Anaconda
REM ------------------------------------------------------------

if exist "%ProgramData%\Anaconda3\Scripts\conda.exe" (
    set "CONDA_ROOT=%ProgramData%\Anaconda3"
    set "CONDA_EXE=%ProgramData%\Anaconda3\Scripts\conda.exe"
    echo Found system Anaconda:
    echo   %CONDA_ROOT%
    goto CONDA_READY
)


REM ------------------------------------------------------------
REM 5. Search PATH specifically for conda.exe
REM ------------------------------------------------------------

for /f "delims=" %%I in ('where conda.exe 2^>nul') do (
    set "CONDA_EXE=%%I"
    goto CONDA_FROM_PATH
)

goto INSTALL_MINICONDA


:CONDA_FROM_PATH

echo Found conda.exe:
echo   %CONDA_EXE%

for %%I in ("%CONDA_EXE%") do set "CONDA_SCRIPTS=%%~dpI"
for %%I in ("%CONDA_SCRIPTS%..") do set "CONDA_ROOT=%%~fI"

goto CONDA_READY


REM ============================================================
REM Install Miniconda
REM ============================================================

:INSTALL_MINICONDA

echo.
echo Conda was not found.
echo.
echo Miniconda will be installed for the current Windows user.
echo.
echo Installation directory:
echo   %CONDA_ROOT%
echo.

echo Downloading Miniconda...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ProgressPreference = 'SilentlyContinue'; " ^
    "Invoke-WebRequest -Uri '%MINICONDA_URL%' -OutFile '%MINICONDA_INSTALLER%'"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to download Miniconda.
    goto BUILD_FAILED
)

if not exist "%MINICONDA_INSTALLER%" (
    echo.
    echo ERROR: Miniconda installer was not downloaded.
    goto BUILD_FAILED
)

echo.
echo Installing Miniconda...
echo.

"%MINICONDA_INSTALLER%" ^
    /InstallationType=JustMe ^
    /RegisterPython=0 ^
    /AddToPath=0 ^
    /S ^
    /D=%CONDA_ROOT%

if errorlevel 1 (
    echo.
    echo ERROR: Miniconda installation failed.
    goto BUILD_FAILED
)

del /q "%MINICONDA_INSTALLER%" >nul 2>&1

if not exist "%CONDA_EXE%" (
    echo.
    echo ERROR: Miniconda installation completed,
    echo but conda.exe was not found.
    echo.
    echo Expected:
    echo   %CONDA_EXE%
    goto BUILD_FAILED
)

echo.
echo Miniconda installed successfully.


REM ============================================================
REM Conda ready
REM ============================================================

:CONDA_READY

echo.
echo ========================================
echo Conda
echo ========================================
echo.
echo Conda executable:
echo   %CONDA_EXE%
echo.
echo Conda root:
echo   %CONDA_ROOT%
echo.


REM ------------------------------------------------------------
REM Verify conda.exe
REM ------------------------------------------------------------

"%CONDA_EXE%" --version

if errorlevel 1 (
    echo.
    echo ERROR: conda.exe could not be executed.
    goto BUILD_FAILED
)


REM ============================================================
REM Check / create Conda environment
REM ============================================================

echo.
echo ========================================
echo Checking Build Environment
echo ========================================
echo.
echo Environment:
echo   %ENV_NAME%
echo.


REM ------------------------------------------------------------
REM Determine whether the environment exists.
REM
REM conda env list produces lines like:
REM
REM base                  C:\Users\david\miniconda3
REM decopro_env           C:\Users\david\miniconda3\envs\decopro_env
REM
REM We only inspect the first column.
REM ------------------------------------------------------------

set "ENV_EXISTS=0"

for /f "tokens=1" %%E in (
    '"%CONDA_EXE%" env list'
) do (
    if /I "%%E"=="%ENV_NAME%" (
        set "ENV_EXISTS=1"
    )
)


REM ------------------------------------------------------------
REM Create environment if it does not exist
REM ------------------------------------------------------------

if "%ENV_EXISTS%"=="0" (

    echo Environment does not exist.
    echo.
    echo Creating environment from:
    echo   %ENV_FILE%
    echo.

    "%CONDA_EXE%" env create ^
        --name "%ENV_NAME%" ^
        --file "%ENV_FILE%"

    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create Conda environment.
        goto BUILD_FAILED
    )

    echo.
    echo Environment created successfully.

) else (

    echo Environment already exists.
)


REM ============================================================
REM Update existing environment
REM ============================================================

echo.
echo Updating environment from environment.yml...
echo.

"%CONDA_EXE%" env update ^
    --name "%ENV_NAME%" ^
    --file "%ENV_FILE%" ^
    --prune

if errorlevel 1 (
    echo.
    echo ERROR: Failed to update Conda environment.
    goto BUILD_FAILED
)

echo.
echo Conda environment is ready.


REM ============================================================
REM Clean previous build
REM ============================================================

echo.
echo ========================================
echo Cleaning Previous Build
echo ========================================
echo.

if exist "%PROJECT_ROOT%\build" (
    echo Removing build directory...
    rmdir /s /q "%PROJECT_ROOT%\build"
)

if exist "%PROJECT_ROOT%\dist" (
    echo Removing dist directory...
    rmdir /s /q "%PROJECT_ROOT%\dist"
)

echo.

REM ============================================================
REM Set Python path for PyInstaller
REM ============================================================

set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

echo.
echo PYTHONPATH:
echo   %PYTHONPATH%
echo.

REM ============================================================
REM Build with PyInstaller
REM ============================================================

echo.
echo ========================================
echo Building %APP_NAME%
echo ========================================
echo.

"%CONDA_EXE%" run ^
    --no-capture-output ^
    --name "%ENV_NAME%" ^
    pyinstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "%APP_NAME%" ^
    --icon "%ICON%" ^
    --add-data "%PNG_ICON%;assets" ^
    "%PROJECT_ROOT%\gui\decopro_app.py"

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed.
    goto BUILD_FAILED
)


REM ============================================================
REM Check executable
REM ============================================================

echo.
echo Checking executable...

if not exist "%EXECUTABLE%" (
    echo.
    echo ERROR: Executable was not created:
    echo   %EXECUTABLE%
    goto BUILD_FAILED
)

echo.
echo Executable created successfully:
echo   %EXECUTABLE%


REM ============================================================
REM Copy PNG next to executable
REM ============================================================

echo.
echo Copying PNG icon...

copy /Y "%PNG_ICON%" "%DIST_DIR%\decopro.png" >nul

if errorlevel 1 (
    echo WARNING: Could not copy decopro.png.
) else (
    echo PNG icon copied successfully.
)


REM ============================================================
REM Find actual Windows Desktop
REM ============================================================

echo.
echo ========================================
echo Creating Desktop Shortcut
echo ========================================
echo.

set "DESKTOP="

for /f "delims=" %%I in ('
    powershell.exe -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"
') do (
    set "DESKTOP=%%I"
)

if not defined DESKTOP (
    echo WARNING: Could not determine Windows Desktop location.
    goto BUILD_SUCCESS
)

echo Desktop:
echo   %DESKTOP%

if not exist "%DESKTOP%" (
    echo.
    echo WARNING: Desktop directory does not exist:
    echo   %DESKTOP%
    goto BUILD_SUCCESS
)

set "SHORTCUT=%DESKTOP%\%APP_NAME%.lnk"

echo.
echo Creating:
echo   %SHORTCUT%
echo.


REM ============================================================
REM Create shortcut
REM ============================================================

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "$shell = New-Object -ComObject WScript.Shell; " ^
    "$shortcut = $shell.CreateShortcut('%SHORTCUT%'); " ^
    "$shortcut.TargetPath = '%EXECUTABLE%'; " ^
    "$shortcut.WorkingDirectory = '%DIST_DIR%'; " ^
    "$shortcut.IconLocation = '%ICON%,0'; " ^
    "$shortcut.Description = 'Decopro Application'; " ^
    "$shortcut.Save()"

if errorlevel 1 (
    echo.
    echo WARNING: Could not create desktop shortcut.
    echo.
    echo The executable was still built successfully.
    goto BUILD_SUCCESS
)

echo.
echo Desktop shortcut created successfully.


REM ============================================================
REM BUILD SUCCESS
REM ============================================================

:BUILD_SUCCESS

echo.
echo.
echo ========================================
echo          BUILD COMPLETE
echo ========================================
echo.
echo Application:
echo   %APP_NAME%
echo.
echo Executable:
echo   %EXECUTABLE%
echo.

if defined SHORTCUT (
    echo Desktop shortcut:
    echo   %SHORTCUT%
    echo.
)

echo ========================================
echo.
echo Press any key to close this window...
pause >nul

exit /b 0


REM ============================================================
REM BUILD FAILED
REM ============================================================

:BUILD_FAILED

echo.
echo.
echo ========================================
echo             BUILD FAILED
echo ========================================
echo.
echo Please review the error above.
echo.
echo Press any key to close this window...
pause >nul

exit /b 1