@echo off
setlocal
cd /d "%~dp0"
echo ============================================
echo   EXPMonitor  build  (PyInstaller, onedir)
echo ============================================
echo.

set "PYTHON=python"
%PYTHON% --version >nul 2>&1
if not errorlevel 1 goto python_found

set "PYTHON=py -3"
%PYTHON% --version >nul 2>&1
if not errorlevel 1 goto python_found

echo Python was not found. Please install Python 3 and add it to PATH.
pause
exit /b 1

:python_found
set "VENV=.build-venv"
if not exist "%VENV%\Scripts\python.exe" (
  echo Creating build virtualenv...
  %PYTHON% -m venv "%VENV%"
  if errorlevel 1 ( echo venv failed & pause & exit /b 1 )
)
set "VPY=%CD%\%VENV%\Scripts\python.exe"
set "PIP_USER=false"

echo [1/3] Installing packages...
"%VPY%" -m pip install --upgrade pip setuptools wheel --quiet
if errorlevel 1 ( echo pip bootstrap failed & pause & exit /b 1 )
"%VPY%" -m pip install ^
  pyinstaller PyQt5 pyqtgraph mss pywin32 Pillow opencv-contrib-python ^
  paddleocr==2.10.0 paddlepaddle==2.6.2 ^
  scikit-image pyclipper lmdb rapidfuzz python-docx beautifulsoup4 ^
  fonttools fire albumentations albucore Cython ^
  --quiet
if errorlevel 1 ( echo pip failed & pause & exit /b 1 )

echo [2/3] Building EXE...
"%VPY%" -m PyInstaller --noconfirm --clean EXPMonitor.spec
if errorlevel 1 ( echo Build failed & pause & exit /b 1 )

echo [3/3] Cleaning up...
if exist build rmdir /s /q build

echo.
echo ============================================
echo   Done. Output folder is  dist\EXPMonitor\
echo   Run the app:  dist\EXPMonitor\EXPMonitor.exe
echo ============================================
echo   PaddleOCR recognition core is bundled inside.
echo   PaddleOCR models may be downloaded on first run.
echo.
pause
