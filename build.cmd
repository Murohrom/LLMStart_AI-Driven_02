@echo off
chcp 65001 >nul
echo ========================================
echo   Сборка Docker образа sarcastic-bot
echo ========================================

echo.
echo Проверка наличия Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ОШИБКА] Docker не установлен или недоступен
    echo Установите Docker Desktop: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo.
echo Сборка образа...
docker build -t sarcastic-bot .

if %ERRORLEVEL% == 0 (
    echo.
    echo [УСПЕХ] Образ sarcastic-bot собран успешно!
    echo.
    echo Для запуска используйте:
    echo   run.cmd
    echo.
    echo Или вручную:
    echo   docker run --env-file .env sarcastic-bot
    echo.
) else (
    echo.
    echo [ОШИБКА] Ошибка при сборке образа
    echo Проверьте логи выше для деталей
    exit /b 1
)

:: Pause только если запущен напрямую (не через call)
if "%1"=="--direct" pause
