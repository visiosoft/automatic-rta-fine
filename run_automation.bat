@echo off
REM Run RTA Automation in Headless Mode (Background)
REM No browser window will appear

echo ========================================
echo RTA Fines Automation - Headless Mode
echo ========================================
echo.
echo Running automation in background...
echo No browser window will appear.
echo.

F:\MyRepo\FetchFine\.venv\Scripts\python.exe F:\MyRepo\FetchFine\run_visible.py

echo.
echo ========================================
echo Automation Completed!
echo ========================================
pause
