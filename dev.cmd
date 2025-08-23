@echo off
chcp 65001 >nul
echo Starting sarcastic bot in development mode...
echo.
echo Checking dependencies...
uv sync
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo.
echo Starting bot...
uv run python src/main.py
if %errorlevel% neq 0 (
    echo Error: Bot failed to start
    pause
    exit /b 1
)
pause
