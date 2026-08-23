@echo off
REM 리본마켓 콘텐츠 자동화 - 구글 드라이브 연결 (윈도우용)
REM 이 파일을 더블클릭하면 설치 마법사가 실행됩니다.
cd /d "%~dp0"
echo.
echo   리본마켓 콘텐츠 자동화 - 설치 준비 중...
echo.
python -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo.
  echo   [!] 파이썬 패키지 설치에 실패했습니다.
  echo       python.org 에서 파이썬을 설치하셨는지 확인해 주세요.
  pause
  exit /b 1
)
python scripts\setup_google.py
echo.
pause
