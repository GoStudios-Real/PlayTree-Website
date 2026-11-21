@echo off
title PLAYTREE Diagnostics
echo ============================================
echo   PLAYTREE Build Diagnostics
echo ============================================
echo.

echo [1] Java (JDK) check:
java -version 2>&1
if errorlevel 1 echo   JAVA NOT FOUND - install JDK 17 from https://adoptium.net/
echo.

echo [2] Gradle check:
where gradle 2>nul
if errorlevel 1 echo   Global gradle not in PATH (OK - wrapper will be used)
echo.

echo [3] ADB check:
where adb 2>nul
if errorlevel 1 echo   ADB not in PATH
echo.

echo [4] Android SDK check:
if exist "C:\Users\RhysC\Android\Sdk" echo   SDK FOUND: C:\Users\RhysC\Android\Sdk
if exist "C:\Users\RhysC\Android\Sdk\platform-tools\adb.exe" echo   ADB FOUND in SDK
if exist "C:\Users\RhysC\Android\Sdk\platforms" echo   SDK platforms folder exists
echo.

echo [5] Project files check:
cd /d "%~dp0android_tv"
if exist "gradlew.bat" echo   gradlew.bat OK
if exist "app\build.gradle" echo   app\build.gradle OK
if exist "local.properties" (
  echo   local.properties OK:
  type local.properties
) else (
  echo   local.properties MISSING
)
echo.

echo ============================================
echo   DIAGNOSTICS COMPLETE
echo ============================================
pause