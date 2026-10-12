@echo off
cd /d "%~dp0"

echo.
echo  ==========================================================
echo    Uploading risk-learning project to GitHub
echo  ==========================================================
echo.
echo   This window will show what happens. Do NOT close it.
echo.
echo  ----------------------------------------------------------
echo.

git push origin main

echo.
echo  ----------------------------------------------------------
echo.
echo   If the last lines show "main" and no red error text, it worked.
echo.
echo   Check your repo here:
echo   https://github.com/01huyifan/risk-learning
echo.
echo   If you see an error, take a screenshot of this window
echo   and send it for help.
echo.
echo  ==========================================================
echo.

pause
