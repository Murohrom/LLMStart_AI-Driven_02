# Саркастический Telegram-бот
# Dockerfile для продакшена

FROM python:3.11-slim

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml ./
COPY requirements.txt ./

# Установка зависимостей через pip
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY test_container_init.py ./

# Создание директории для логов
RUN mkdir -p logs

# Переменные окружения по умолчанию
ENV LOG_LEVEL=INFO
ENV LOG_FILE=logs/bot.log

# Пользователь без привилегий для безопасности
RUN adduser --disabled-password --gecos '' botuser && \
    chown -R botuser:botuser /app
USER botuser

# Healthcheck - проверка, что процесс Python запущен
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep python || exit 1

# Точка входа
CMD ["python", "src/main.py"]
