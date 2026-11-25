@echo off
cd /d "%~dp0"
echo SCHOOL NOTICEBOARD - Windows starter
if not exist ".venv\Scripts\python.exe" (
    echo Creating local Python environment...
    py -m venv .venv
    if errorlevel 1 goto failed
)
echo Installing dependencies (first run needs internet)...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Starting server on http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py
echo Server stopped.
pause
exit /b 0
:failed
echo Setup failed. Read 02_INSTALL_AND_SETUP.txt and 09_FIX_COMMON_ERRORS.txt
pause
exit /b 1
