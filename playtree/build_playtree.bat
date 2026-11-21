@echo off
setlocal EnableExtensions
title PLAYTREE Build
cd /d "%~dp0" || exit /b 1

echo ============================================
echo   PLAYTREE Build Script
echo   Version: 1.0.1
echo   Target: dist\PLAYTREE.exe
echo ============================================
echo.

echo [1/5] Cleaning previous builds...
for %%d in (dist build __pycache__) do (
  if exist "%%d" rmdir /s /q "%%d" 2>nul
)
echo Done.
echo.

echo [2/5] Installing dependencies...
python -m pip install --upgrade pyinstaller pygame-ce
if errorlevel 1 (
  echo ERROR: Failed to install dependencies.
  pause
  exit /b 1
)
echo Done.
echo.

echo [3/5] Building PLAYTREE.exe...
python build_exe.py
if not exist dist\PLAYTREE.exe (
  echo.
  echo BUILD FAILED - dist\PLAYTREE.exe was not created.
  pause
  exit /b 1
)
echo Done.
echo.

echo [4/5] Copying to website/downloads...
if not exist "..\website\downloads" mkdir "..\website\downloads"
copy /Y dist\PLAYTREE.exe "..\website\downloads\PLAYTREE.exe" >nul
if exist "..\website\downloads\PLAYTREE.exe" (
  echo Copied to website\downloads\PLAYTREE.exe
) else (
  echo WARNING: Could not copy to website\downloads
)
echo.

echo [5/5] Verifying build...
for %%F in (dist\PLAYTREE.exe) do set SIZE=%%~zF
set /a SIZE_MB=%SIZE%/1048576
echo EXE size: %SIZE_MB% MB
echo.

echo ============================================
echo   BUILD COMPLETE
echo   EXE:  dist\PLAYTREE.exe
echo   Web:  website\downloads\PLAYTREE.exe
echo ============================================
echo.
echo Next steps:
echo   1. Run push_to_github.bat to deploy the website
echo   2. Run create_github_release.bat to publish a release
echo.
pause