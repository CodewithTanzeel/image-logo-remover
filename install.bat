@echo off
REM rmlogo Installer for Windows
REM Double-click this file to install rmlogo completely offline
REM
REM This script:
REM   1. Installs all dependencies from the wheels/ folder
REM   2. Installs rmlogo in editable mode
REM   3. Verifies installation
REM
REM Requirements: Python 3.9+ must be installed
REM               pip must be available in PATH

echo.
echo ============================================================
echo  rmlogo Installer v2.1.0
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.9 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Detected Python:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

echo.
echo Installing dependencies from offline wheels...
echo.

REM Install from wheels folder (completely offline)
pip install --no-index --find-links=wheels -e . --quiet

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Troubleshooting:
    echo   1. Make sure you have Python 3.9+ installed
    echo   2. Check that wheels/ folder exists in this directory
    echo   3. Try running as Administrator
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.

REM Verify installation
rmlogo --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: rmlogo command not found
    echo.
    echo The package may not be fully installed.
    echo Try the manual install command:
    echo   pip install --no-index --find-links=wheels -e .
    echo.
    pause
    exit /b 1
)

echo Success! rmlogo is now installed and ready to use.
echo.
echo Quick test:
rmlogo --version
echo.
echo Next steps:
echo   1. Open PowerShell
echo   2. Run: rmlogo image.jpg
echo   3. Read USER_MANUAL.md for full documentation
echo.
echo For help:
echo   rmlogo --help
echo.
pause
exit /b 0
