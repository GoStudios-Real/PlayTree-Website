@echo off
setlocal EnableExtensions
title PLAYTREE Gradle Wrapper
cd /d "%~dp0"

set "GRADLE_BAT=C:\Users\RhysC\Downloads\PlayTree 2\PLAYTREE-1.0.1\PLAYTREE-1.0.1\gradle-8.5\bin\gradle.bat"

if exist "%GRADLE_BAT%" (
  call "%GRADLE_BAT%" %*
  exit /b %errorlevel%
)

echo Gradle not found at %GRADLE_BAT%
echo Please check the path.
pause
exit /b 1