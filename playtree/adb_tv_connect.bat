@echo off
setlocal EnableExtensions
title PLAYTREE ADB TV Connect
cd /d "%~dp0"

echo ============================================
echo   PLAYTREE - Connect to Google TV via ADB
echo ============================================
echo.
echo   TV IP from screen: 192.168.0.78
echo.
echo   BEFORE RUNNING, on your TV:
echo   1. Settings > System > About
echo   2. Click "Build" 7 times to enable Developer Options
echo   3. Settings > Developer options > USB/Network debugging = ON
echo   4. Reboot the TV
echo.
echo   NOTE: Google TV Streamer may need ADB over network
echo   enabled in Developer options -> "Network debugging"
echo.
pause

set "TV_IP=192.168.0.78"
set "ADB="

rem Try to find adb.exe
where adb >nul 2>&1
if not errorlevel 1 (
  set "ADB=adb"
) else (
  if exist "%ANDROID_HOME%\platform-tools\adb.exe" set "ADB=%ANDROID_HOME%\platform-tools\adb.exe"
  if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
  if exist "C:\adb\adb.exe" set "ADB=C:\adb\adb.exe"
)

if not defined ADB (
  echo ERROR: adb.exe not found.
  echo Install Android platform-tools and add to PATH, or place adb.exe in C:\adb\
  echo Download: https://developer.android.com/studio/releases/platform-tools
  pause
  exit /b 1
)
echo Using ADB: %ADB%
echo.

echo Connecting to TV at %TV_IP%:5555 ...
"%ADB%" kill-server
"%ADB%" start-server
"%ADB%" connect %TV_IP%:5555
echo.

echo Connected devices:
"%ADB%" devices
echo.

echo Testing connection...
"%ADB%" -s %TV_IP%:5555 shell getprop ro.product.model 2>nul
if errorlevel 1 (
  echo.
  echo WARNING: Could not connect. Check:
  echo   - TV is on the same Wi-Fi network as this PC
  echo   - Network debugging is enabled on the TV
  echo   - TV IP is still %TV_IP%
  echo   - Accept the ADB prompt on the TV screen if shown
) else (
  echo.
  echo SUCCESS! TV connected via ADB.
  echo You can now run install_on_tv.bat
)
echo.
pause