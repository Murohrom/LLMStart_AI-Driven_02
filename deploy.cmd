@echo off
echo ========================================
echo   Деплой sarcastic-bot
echo ========================================

echo.
echo [ШАГ 1] Проверка окружения...

:: Проверка Docker
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ОШИБКА] Docker не установлен
    pause
    exit /b 1
)

:: Проверка .env файла
if not exist .env (
    echo [ОШИБКА] Файл .env не найден
    echo Создайте .env файл с производственными настройками
    pause
    exit /b 1
)

:: Проверка обязательных переменных
findstr /i "TELEGRAM_BOT_TOKEN" .env >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ОШИБКА] TELEGRAM_BOT_TOKEN не найден в .env
    pause
    exit /b 1
)

findstr /i "OPENROUTER_API_KEY" .env >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ОШИБКА] OPENROUTER_API_KEY не найден в .env
    pause
    exit /b 1
)

echo [УСПЕХ] Окружение проверено

echo.
echo [ШАГ 2] Остановка старых контейнеров...
docker stop sarcastic-bot-container 2>nul
docker rm sarcastic-bot-container 2>nul
docker stop sarcastic-bot-dev 2>nul
docker rm sarcastic-bot-dev 2>nul

echo.
echo [ШАГ 3] Сборка продакшн образа...
docker build -t sarcastic-bot:latest .
if %ERRORLEVEL% neq 0 (
    echo [ОШИБКА] Сборка образа завершилась с ошибкой
    pause
    exit /b 1
)

echo.
echo [ШАГ 4] Тестовый запуск...
docker run --rm --env-file .env -d --name sarcastic-bot-test sarcastic-bot:latest
if %ERRORLEVEL% neq 0 (
    echo [ОШИБКА] Тестовый запуск неудачен
    pause
    exit /b 1
)

:: Ждем 10 секунд и проверяем статус
timeout /t 10 /nobreak >nul
docker ps --filter "name=sarcastic-bot-test" --format "table {{.Names}}\t{{.Status}}" | findstr "sarcastic-bot-test"
if %ERRORLEVEL% neq 0 (
    echo [ОШИБКА] Контейнер не запустился или упал
    docker logs sarcastic-bot-test
    docker rm -f sarcastic-bot-test 2>nul
    pause
    exit /b 1
)

echo [УСПЕХ] Тестовый запуск прошел успешно
docker stop sarcastic-bot-test >nul 2>&1
docker rm sarcastic-bot-test >nul 2>&1

echo.
echo [ШАГ 5] Продакшн запуск...
docker run -d ^
    --name sarcastic-bot-prod ^
    --env-file .env ^
    -v "%cd%\logs:/app/logs" ^
    --restart unless-stopped ^
    sarcastic-bot:latest

if %ERRORLEVEL% == 0 (
    echo.
    echo ========================================
    echo [УСПЕХ] Деплой завершен успешно!
    echo ========================================
    echo.
    echo Контейнер: sarcastic-bot-prod
    echo Логи:      docker logs sarcastic-bot-prod
    echo Остановка: docker stop sarcastic-bot-prod
    echo Статус:    docker ps
    echo.
    echo Файлы логов также доступны в папке logs/
) else (
    echo [ОШИБКА] Ошибка при запуске продакшн контейнера
    pause
    exit /b 1
)

pause
