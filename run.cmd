@echo off
chcp 65001 >nul
echo ========================================
echo   Запуск sarcastic-bot в Docker
echo ========================================

echo.
echo Проверка наличия .env файла...
if not exist .env (
    echo [ПРЕДУПРЕЖДЕНИЕ] Файл .env не найден
    echo Создаю из примера...
    if exist env.example (
        copy env.example .env
        echo [СОЗДАН] .env файл создан из env.example
        echo [ВАЖНО] Отредактируйте .env файл с вашими токенами!
        echo.
        pause
    ) else (
        echo [ОШИБКА] Файл env.example не найден
        echo Создайте .env файл с необходимыми переменными
        pause
        exit /b 1
    )
)

echo.
echo Проверка наличия образа...
docker image inspect sarcastic-bot >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Образ sarcastic-bot не найден
    echo Запускаю сборку...
    call build.cmd
    if %ERRORLEVEL% neq 0 (
        echo [ОШИБКА] Не удалось собрать образ
        pause
        exit /b 1
    )
)

echo.
echo Остановка предыдущего контейнера (если есть)...
docker stop sarcastic-bot-container 2>nul
docker rm sarcastic-bot-container 2>nul

echo.
echo Запуск контейнера...
docker run -d ^
    --name sarcastic-bot-container ^
    --env-file .env ^
    -v "%CD%\logs:/app/logs" ^
    --restart unless-stopped ^
    sarcastic-bot

if %ERRORLEVEL% == 0 (
    echo.
    echo [УСПЕХ] Бот запущен в контейнере!
    echo.
    echo Полезные команды:
    echo   docker logs sarcastic-bot-container     - просмотр логов
    echo   docker stop sarcastic-bot-container     - остановка бота
    echo   docker restart sarcastic-bot-container  - перезапуск бота
    echo.
    echo Логи также доступны в папке logs/
) else (
    echo.
    echo [ОШИБКА] Не удалось запустить контейнер
    echo Проверьте конфигурацию и логи Docker
    pause
    exit /b 1
)

pause
