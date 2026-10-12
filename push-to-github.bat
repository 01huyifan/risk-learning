@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo  ==========================================================
echo    Upload risk-learning to GitHub
echo  ==========================================================
echo.

where git >nul 2>&1
if errorlevel 1 goto NOGIT

echo   What did you change this time?
echo   Type a short note, then press Enter.
echo   (Just press Enter to skip)
echo.
set "MSG="
set /p "MSG=  Note: "
if "%MSG%"=="" set "MSG=update"

echo.
echo  ----------------------------------------------------------
echo   [1/3] Collecting changes ...
git add -A
git diff --cached --quiet
if not errorlevel 1 goto SKIPCOMMIT

echo   [2/3] Saving a snapshot ...
git commit -m "%MSG%"
if errorlevel 1 goto FAIL
goto DOPUSH

:SKIPCOMMIT
echo   [2/3] No new changes to save.

:DOPUSH
echo   [3/3] Uploading to GitHub ...
git push origin main
if errorlevel 1 goto FAIL

echo.
echo  ----------------------------------------------------------
echo   DONE. Your code is online:
echo   https://github.com/01huyifan/risk-learning
echo.
echo  ==========================================================
echo.
pause
exit /b 0

:FAIL
echo.
echo   [!] Something went wrong. Screenshot this window.
echo       Your changes are already saved on this computer.
echo       Simply run this file again to retry.
echo.
pause
exit /b 1

:NOGIT
echo   [!] Git was NOT found on this computer.
echo       Install Git first, then run this file again.
echo.
pause
exit /b 1
