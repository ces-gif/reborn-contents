@echo off
rem ---------------------------------------------------------------
rem  Reborn Market content automation - setup launcher (Windows)
rem  NOTE: keep this file ASCII-only. cmd.exe mangles non-ASCII
rem        batch files and tries to run the garbled text as commands.
rem        All Korean guidance lives in scripts/setup_google.py.
rem ---------------------------------------------------------------
cd /d "%~dp0"

set "PY="
py -3 -c "import sys" >nul 2>&1
if %errorlevel%==0 set "PY=py -3"
if defined PY goto haspy

python -c "import sys" >nul 2>&1
if %errorlevel%==0 set "PY=python"
if defined PY goto haspy

echo.
echo   Python is not installed.
echo   1. A download page will open. Click the yellow Download button.
echo   2. In the installer, CHECK "Add python.exe to PATH" at the bottom.
echo   3. Run this setup.bat again.
echo.
start "" "https://www.python.org/downloads/"
pause
exit /b 1

:haspy
echo.
echo   Reborn Market - setup
echo.
%PY% --version
echo.
echo   Installing packages (1-2 minutes on first run)...
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if not %errorlevel%==0 goto pipfail

%PY% scripts\setup_google.py
echo.
pause
exit /b 0

:pipfail
echo.
echo   Package install failed. Check your internet connection and retry.
pause
exit /b 1
