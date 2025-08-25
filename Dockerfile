# Саркастический Telegram-бот
# Dockerfile для продакшена

FROM python:3.11-slim

# Установка uv для быстрого управления зависимостями
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml ./
COPY uv.lock ./

# Проверка наличия файлов
RUN ls -la pyproject.toml uv.lock

# Установка зависимостей
RUN uv sync --frozen --no-cache --no-dev

# Копирование исходного кода
COPY src/ ./src/
COPY prompts/ ./prompts/

# Создание директории для логов
RUN mkdir -p logs

# Переменные окружения по умолчанию
ENV LOG_LEVEL=INFO
ENV LOG_FILE=logs/bot.log

# Пользователь без привилегий для безопасности
RUN adduser --disabled-password --gecos '' botuser && \
    chown -R botuser:botuser /app
USER botuser

# Точка входа
CMD ["uv", "run", "python", "src/main.py"]
