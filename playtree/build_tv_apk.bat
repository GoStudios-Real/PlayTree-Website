@echo off
title PLAYTREE TV APK Build
cd /d "%~dp0android_tv"

echo ============================================
echo   PLAYTREE TV - Build APK with Gradle
echo ============================================
echo.

set "GRADLE_BAT=C:\Users\RhysC\Downloads\PlayTree 2\PLAYTREE-1.0.1\PLAYTREE-1.0.1\gradle-8.5\bin\gradle.bat"
if not exist "%GRADLE_BAT%" set "GRADLE_BAT=gradlew.bat"

echo Running: %GRADLE_BAT% assembleDebug
echo Building... please wait.
echo.

call "%GRADLE_BAT%" assembleDebug > ..\build_tv_log.txt 2>&1

echo.
echo ============================================
echo   Build finished.
echo ============================================
echo.
if exist "app\build\outputs\apk\debug\app-debug.apk" (
  echo APK FOUND!
  if not exist "..\bin" mkdir "..\bin"
  copy /Y "app\build\outputs\apk\debug\app-debug.apk" "..\bin\PLAYTREE-TV.apk"
  echo Copied to bin\PLAYTREE-TV.apk
) else (
  echo APK NOT FOUND. Here is the error log:
  echo ----------------------------------------
  type ..\build_tv_log.txt
)
echo.
pause