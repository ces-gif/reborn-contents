@echo off
setlocal
chcp 65001 >nul
REM ============================================================
REM  리본마켓 콘텐츠 자동화 - 구글 드라이브 연결 (윈도우용)
REM  이 파일을 더블클릭하면 설치 마법사가 실행됩니다.
REM ============================================================
cd /d "%~dp0"

echo.
echo   ============================================
echo    리본마켓 콘텐츠 자동화 - 설치 마법사
echo   ============================================
echo.

REM --- 파이썬 찾기: py 런처 먼저, 없으면 python ---
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
  python --version >nul 2>&1 && set "PY=python"
)

REM 윈도우 스토어 껍데기(python.exe 스텁)를 걸러낸다
if defined PY (
  %PY% -c "import sys" >nul 2>&1 || set "PY="
)

if not defined PY (
  echo   [!] 파이썬이 설치되어 있지 않습니다.
  echo.
  echo   1) 브라우저가 열리면 노란색 [Download Python] 버튼을 누르세요.
  echo   2) 설치 창 맨 아래 [Add python.exe to PATH] 를 반드시 체크하세요.
  echo   3) 설치가 끝나면 이 setup.bat 을 다시 더블클릭하세요.
  echo.
  start "" "https://www.python.org/downloads/"
  pause
  exit /b 1
)

echo   파이썬 확인:
%PY% --version
echo.
echo   필요한 패키지를 설치합니다. 처음 한 번만 1~2분 걸립니다...
echo.

%PY% -m pip install --quiet --disable-pip-version-check --upgrade pip
%PY% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo.
  echo   [!] 패키지 설치에 실패했습니다.
  echo       인터넷 연결을 확인하고 다시 시도해 주세요.
  pause
  exit /b 1
)

echo   준비 완료. 마법사를 시작합니다.
echo.
%PY% scripts\setup_google.py
echo.
pause
