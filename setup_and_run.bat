@echo off
chcp 65001 >nul
title LiDAR Lift Monitor - Setup and Run

echo   LiDAR Lift Monitor - Setup and Run
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ first.
    pause
    exit /b 1
)
echo [OK] Python found:
python --version
echo.

:: Create venv if not exists
if not exist "new_venv\Scripts\python.exe" (
    echo [STEP 1] Creating virtual environment...
    python -m venv new_venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
    echo [OK] venv created.
) else (
    echo [OK] venv already exists.
)
echo.

:: Activate venv and install dependencies
echo [STEP 2] Installing dependencies...
call new_venv\Scripts\activate.bat
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] All dependencies installed.
echo.

:: Run the app
echo [STEP 3] Launching LiDAR Lift Monitor...
python src\main.py

echo.
echo   App exited.
