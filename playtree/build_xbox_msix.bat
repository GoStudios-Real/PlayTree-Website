@echo off
title PLAYTREE Xbox/MSIX Prep
cd /d "%~dp0"
echo Building Windows EXE first...
call build_playtree.bat
if not exist dist\PLAYTREE.exe (
  echo EXE build failed. Fix errors before MSIX packaging.
  pause
  exit /b 1
)
echo.
echo EXE ready: dist\PLAYTREE.exe
echo.
echo Next steps for Xbox/Microsoft Store:
echo 1. Install MSIX Packaging Tool (Microsoft Store).
echo 2. Create package from dist\PLAYTREE.exe.
echo 3. Upload to Microsoft Partner Center.
echo 4. See XBOX_README.md for details.
pause