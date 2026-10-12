@echo off
cd /d "%~dp0"

echo.
echo  ==========================================================
echo    Uploading risk-learning project to GitHub
echo  ==========================================================
echo.

where git >nul 2>&1
if errorlevel 1 goto NOGIT

echo   Git found. Starting upload ...
echo  ----------------------------------------------------------
echo.

git push origin main

echo.
echo  ----------------------------------------------------------
echo.
echo   SUCCESS looks like this:  a line with "main", no red text.
echo.
echo   Check your repo here:
echo   https://github.com/01huyifan/risk-learning
echo.
echo   If you see red error text, screenshot this window.
echo.
echo  ==========================================================
echo.
pause
exit /b 0

:NOGIT
echo   [!] Git was NOT found on this computer.
echo.
echo   How to fix:
echo     1. Install Git first (use the installer on your Desktop)
echo     2. Close this window
echo     3. Double-click this file again
echo.
echo  ==========================================================
echo.
pause
exit /b 1
