@echo off
title PLAYTREE Local Server
cd /d "%~dp0\..\website"

echo ============================================
echo   PLAYTREE Local Web Server
echo ============================================
echo.
echo Serving website on port 8000
echo.
echo Find your PC's IP with: ipconfig
echo Then set TV_URL in MainActivity.java to:
echo   http://YOUR_PC_IP:8000/tv.html
echo.
echo Press Ctrl+C to stop.
echo.
python -m http.server 8000
pause