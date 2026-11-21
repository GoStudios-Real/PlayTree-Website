@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title PLAYTREE GitHub Release

echo ============================================
echo   PLAYTREE GitHub Release Creator
echo ============================================
echo.

REM Check if gh CLI is installed
where gh >nul 2>&1
if errorlevel 1 (
  echo ERROR: GitHub CLI (gh) is not installed.
  echo Download from: https://cli.github.com/
  echo.
  echo Alternatively, create a release manually at:
  echo https://github.com/GoStudios-Real/PlayTree-Website/releases/new
  pause
  exit /b 1
)

REM Check if EXE exists
if not exist "playtree\dist\PLAYTREE.exe" (
  echo ERROR: playtree\dist\PLAYTREE.exe not found.
  echo Run build_playtree.bat first.
  pause
  exit /b 1
)

REM Get version from version.json
for /f "delims=" %%v in ('python -c "import json; print(json.load(open('playtree/version.json'))['version'])" 2^>nul') do set "VERSION=%%v"
if not defined VERSION set "VERSION=1.0.1"

echo Creating release v%VERSION%...
echo.

REM Create the release with the EXE attached
gh release create "v%VERSION%" "playtree\dist\PLAYTREE.exe" ^
  --repo GoStudios-Real/PlayTree-Website ^
  --title "PLAYTREE v%VERSION%" ^
  --notes "PLAYTREE v%VERSION% - Awaken. Rebuild. Restore Balance." ^
  --latest

if errorlevel 1 (
  echo.
  echo Release creation failed. Check gh auth status.
  echo Run: gh auth login
  pause
  exit /b 1
)

echo.
echo ============================================
echo   Release v%VERSION% created successfully!
echo   https://github.com/GoStudios-Real/PlayTree-Website/releases/tag/v%VERSION%
echo ============================================
pause