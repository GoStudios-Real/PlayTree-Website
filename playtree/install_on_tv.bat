@echo off
setlocal EnableExtensions
title PLAYTREE - Install on TV
cd /d "%~dp0"

echo ============================================
echo   PLAYTREE - Install APK on Google TV
echo ============================================
echo.

set "TV_IP=192.168.0.78"
set "PKG=org.gostudios.playtree.tv"
set "ADB="

where adb >nul 2>&1
if not errorlevel 1 (
  set "ADB=adb"
) else (
  if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
  if exist "C:\adb\adb.exe" set "ADB=C:\adb\adb.exe"
)

if not defined ADB (
  echo ERROR: adb.exe not found. Install Android platform-tools first.
  pause
  exit /b 1
)

set "APK="
if exist "bin\PLAYTREE-TV.apk" set "APK=bin\PLAYTREE-TV.apk"
if exist "android_tv\app\build\outputs\apk\debug\app-debug.apk" set "APK=android_tv\app\build\outputs\apk\debug\app-debug.apk"

if not defined APK (
  echo No APK found. Building with Gradle first...
  echo.
  call build_tv_apk.bat
  if exist "bin\PLAYTREE-TV.apk" set "APK=bin\PLAYTREE-TV.apk"
  if not defined APK (
    echo ERROR: Could not build APK. Build manually then retry.
    pause
    exit /b 1
  )
)

echo APK: %APK%
echo.

echo Connecting to TV at %TV_IP%...
"%ADB%" connect %TV_IP%:5555
echo.

echo Checking connection...
"%ADB%" -s %TV_IP%:5555 get-state 2>nul
if errorlevel 1 (
  echo ERROR: TV not connected. Run adb_tv_connect.bat first.
  echo Make sure Network debugging is ON on the TV.
  pause
  exit /b 1
)

echo Installing %APK% ...
"%ADB%" -s %TV_IP%:5555 install -r "%APK%"
if errorlevel 1 (
  echo Retrying with -d (downgrade allowed)...
  "%ADB%" -s %TV_IP%:5555 install -r -d "%APK%"
)
if errorlevel 1 (
  echo INSTALL FAILED. Check errors above.
) else (
  echo.
  echo INSTALL SUCCESSFUL!
  echo Launching PLAYTREE TV...
  "%ADB%" -s %TV_IP%:5555 shell monkey -p %PKG% 1
  echo.
  echo If the app shows a dark screen, the website URL may not be live.
  echo Run serve_website_local.bat and update TV_URL in MainActivity.java.
)
echo.
pause