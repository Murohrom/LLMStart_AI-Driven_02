# Запуск sarcastic-bot в Docker
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Запуск sarcastic-bot в Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""

# Проверка наличия .env файла
Write-Host "Проверка наличия .env файла..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "[OK] .env файл найден" -ForegroundColor Green
} else {
    Write-Host "[ОШИБКА] Файл .env не найден" -ForegroundColor Red
    Write-Host "Создайте .env файл с необходимыми переменными окружения:" -ForegroundColor Red
    Write-Host "  - TELEGRAM_BOT_TOKEN" -ForegroundColor Red
    Write-Host "  - OPENROUTER_API_KEY" -ForegroundColor Red
    Write-Host "Используйте env.example как шаблон" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""

# Проверка наличия образа
Write-Host "Проверка наличия образа..." -ForegroundColor Yellow
$imageExists = docker image inspect sarcastic-bot 2>$null
if ($imageExists -and $imageExists -ne "[]" -and $imageExists.Length -gt 0) {
    Write-Host "[OK] Образ sarcastic-bot найден" -ForegroundColor Green
} else {
    Write-Host "[ПРЕДУПРЕЖДЕНИЕ] Образ sarcastic-bot не найден" -ForegroundColor Yellow
    Write-Host "Запускаю сборку..." -ForegroundColor Yellow
    
    # Запуск сборки
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Сборка Docker образа sarcastic-bot" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "Проверка наличия Docker..." -ForegroundColor Yellow
    
    try {
        $dockerVersion = docker --version
        Write-Host "[OK] Docker найден: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "[ОШИБКА] Docker не установлен или недоступен" -ForegroundColor Red
        Write-Host "Установите Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
    
    Write-Host ""
    Write-Host "Сборка образа..." -ForegroundColor Yellow
    docker build -t sarcastic-bot .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[УСПЕХ] Образ sarcastic-bot собран успешно!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[ОШИБКА] Ошибка при сборке образа" -ForegroundColor Red
        Write-Host "Проверьте логи выше для деталей" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
}

Write-Host ""

# Остановка предыдущего контейнера
Write-Host "Остановка предыдущего контейнера (если есть)..." -ForegroundColor Yellow
docker stop sarcastic-bot-container 2>$null
docker rm sarcastic-bot-container 2>$null

Write-Host ""

# Запуск контейнера
Write-Host "Запуск контейнера..." -ForegroundColor Yellow
docker run -d `
    --name sarcastic-bot-container `
    --platform linux/amd64 `
    --env-file .env `
    -v "${PWD}/logs:/app/logs" `
    --restart unless-stopped `
    sarcastic-bot

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[УСПЕХ] Бот запущен в контейнере!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Полезные команды:" -ForegroundColor Cyan
    Write-Host "  docker logs sarcastic-bot-container     - просмотр логов" -ForegroundColor White
    Write-Host "  docker stop sarcastic-bot-container     - остановка бота" -ForegroundColor White
    Write-Host "  docker restart sarcastic-bot-container  - перезапуск бота" -ForegroundColor White
    Write-Host ""
    Write-Host "Логи также доступны в папке logs/" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "[ОШИБКА] Не удалось запустить контейнер" -ForegroundColor Red
    Write-Host "Проверьте конфигурацию и логи Docker" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Read-Host "Нажмите Enter для завершения"
