@echo off
echo Installing dependencies...
uv sync --no-dev
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
pause
