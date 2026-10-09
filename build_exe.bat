@echo off
REM ============================================================
REM  StudyDesk Pro - Windows EXE Build Script
REM  ============================================================
REM  Usage:  build_exe.bat
REM  Output: dist\StudyDeskPro\StudyDeskPro.exe
REM ============================================================

echo.
echo ============================================
echo   StudyDesk Pro - Build Windows EXE
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip install pyinstaller matplotlib Pillow --quiet 2>nul

echo [2/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/4] Building executable with PyInstaller...
python -m PyInstaller StudyDeskPro.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed. Check the output above.
    pause
    exit /b 1
)

echo [4/4] Build complete!
echo.
echo ============================================
echo   Output: dist\StudyDeskPro\StudyDeskPro.exe
echo ============================================
echo.
echo You can run the application by double-clicking
echo   StudyDeskPro.exe
echo.
pause