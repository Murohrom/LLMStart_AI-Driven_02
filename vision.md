# Техническое видение проекта: Мультимодальный ИИ-консультант

## Обзор проекта

Разработка полноценного мультимодального ИИ-ассистента в виде Telegram-бота, который предоставляет консультации через различные типы контента: текст, изображения, аудио и голосовые сообщения. Бот поддерживает локальные модели для обеспечения приватности и может адаптироваться под конкретные задачи пользователя.

## Технологии

### Основной стек
- **Python 3.11+** - основной язык разработки
- **aiogram** - современная асинхронная библиотека для работы с Telegram Bot API
- **Ollama** - локальные LLM модели для приватной обработки
- **OpenRouter API** - облачные LLM для расширенных возможностей
- **aiohttp** - асинхронные HTTP запросы
- **python-dotenv** - управление переменными окружения
- **logging** (встроенный) - система логгирования

### Мультимодальные технологии
- **Pillow/PIL** - обработка изображений
- **OpenCV** - компьютерное зрение
- **SpeechRecognition** - распознавание речи (STT)

- **whisper** - локальное распознавание речи

### Дополнительные инструменты
- **Docker** - контейнеризация для продакшена
- **Railway** - хостинг платформа
- **SQLite/PostgreSQL** - хранение данных пользователей
- **Redis** - кэширование и сессии

## Принципы разработки

1. **KISS (Keep It Simple, Stupid)** - максимальная простота решений
2. **Модульная архитектура** - разделение функциональности по модулям
3. **Приватность прежде всего** - локальные модели для чувствительных данных
4. **Fail Fast** - быстрое обнаружение ошибок
5. **Минимальные зависимости** - только необходимые библиотеки
6. **Конфигурация через переменные окружения** - простая настройка
7. **Логгирование критических событий** - только важные события
8. **Graceful degradation** - бот работает даже при проблемах с внешними сервисами

## Структура проекта

```
multimodal_ai_bot/
├── main.py                 # Точка входа, запуск бота
├── config/
│   └── settings.py         # Настройки и конфигурация
├── bot/
│   ├── handlers.py         # Обработчики сообщений Telegram
│   └── middleware.py       # Промежуточное ПО для обработки
├── llm/
│   ├── client.py           # Клиент для работы с LLM
│   ├── local_models.py     # Локальные модели (Ollama)
│   └── cloud_models.py     # Облачные модели (OpenRouter)
├── multimodal/
│   ├── image_processor.py  # Обработка изображений
│   ├── audio_processor.py  # Обработка аудио
│   └── audio_processor.py # Обработка аудио
├── storage/
│   ├── database.py         # Работа с базой данных
│   └── cache.py           # Кэширование
├── utils/
│   ├── logger.py           # Настройка логгирования
│   ├── validators.py       # Валидация данных
│   └── formatters.py       # Форматирование ответов
├── prompts/
│   ├── system.txt          # Системный промпт
│   └── templates/          # Шаблоны промптов
├── models/                 # Локальные модели
├── logs/                   # Директория для логов
├── .env                    # Переменные окружения (локально)
├── env.example             # Пример конфигурации
├── pyproject.toml          # Конфигурация проекта и зависимости
├── uv.lock                 # Фиксация версий зависимостей
├── Makefile                # Автоматизация команд сборки
├── Dockerfile              # Контейнеризация
├── docker-compose.yml      # Для локальной разработки
├── railway.toml            # Конфигурация Railway
└── .github/workflows/      # CI/CD пайплайны
    └── deploy.yml
```

## Архитектура системы

### Компоненты и поток данных

```
[Пользователь] 
    ↓ (текст/фото/аудио)
[Telegram API]
    ↓
[aiogram Bot] → [Message Handler]
    ↓
[Multimodal Processor] → [Content Router]
    ↓
[LLM Client] → [Local/Cloud Models]
    ↓ (мультимодальный ответ)
[Response Formatter] 
    ↓
[aiogram Bot] → [Telegram API]
    ↓
[Пользователь]
```

### Ключевые особенности
- **Webhook/Polling** для получения сообщений
- **Мультимодальная обработка** - поддержка всех типов контента
- **Гибридная архитектура** - локальные и облачные модели
- **Асинхронная обработка** благодаря aiogram
- **Кэширование** для оптимизации производительности

## Модель данных

### База данных пользователей
```python
users = {
    "user_id": {
        "preferences": {
            "response_format": "text|image|audio|voice",
            "privacy_level": "local|cloud|hybrid",
            "language": "ru|en"
        },
        "session": {
            "current_context": "conversation_context",
            "last_activity": datetime
        }
    }
}
```

### История диалогов
```python
conversations = {
    "user_id": [
        {
            "timestamp": datetime,
            "input_type": "text|image|audio",
            "input_content": "content_hash",
            "output_type": "text|image|audio|voice",
            "output_content": "content_hash",
            "model_used": "local|cloud"
        }
    ]
}
```

### Кэш контента
```python
content_cache = {
    "content_hash": {
        "type": "text|image|audio",
        "data": "binary_or_text_data",
        "metadata": {
            "size": "file_size",
            "format": "file_format",
            "created": datetime
        },
        "ttl": 3600  # 1 час
    }
}
```

## Работа с LLM

### Конфигурация моделей

#### Локальные модели (Ollama)
- **Текст**: `llama3.2:3b`, `mistral:7b`, `codellama:7b`
- **Изображения**: `llava:7b`, `bakllava:7b`
- **Аудио**: `whisper:base`, `whisper:small`

#### Облачные модели (OpenRouter)
- **Текст**: `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`
- **Изображения**: `anthropic/claude-3-5-sonnet`
- **Аудио**: `openai/whisper-1`

### Системный промпт
```
"Ты - мультимодальный ИИ-консультант. Твоя задача - помогать пользователям 
через различные форматы контента: текст, изображения, аудио и голосовые сообщения.

Основные принципы:
1. Адаптируйся под предпочтения пользователя
2. Используй локальные модели для приватных данных
3. Предоставляй ответы в запрошенном формате
4. Сохраняй контекст диалога
5. Обеспечивай высокое качество консультаций

Поддерживаемые форматы ответов:
- Текст: структурированные и понятные ответы
- Изображения: визуализация концепций и решений
- Аудио: голосовые консультации
- Гибрид: комбинация форматов по запросу"
```

### Обработка ошибок
- При недоступности локальных моделей: fallback на облачные
- При таймауте API: уведомление пользователя
- При ошибке обработки: graceful degradation с текстовым ответом

## Мультимодальная обработка

### Обработка изображений
```python
class ImageProcessor:
    def analyze_image(self, image_data):
        # Анализ изображения через локальные модели
        # Извлечение текста, объектов, сцен
        pass
```

### Обработка аудио
```python
class AudioProcessor:
    def speech_to_text(self, audio_data):
        # Распознавание речи через whisper
        # Локальная обработка
        pass
    
    def text_to_speech(self, text):
        # Распознавание речи через Whisper
        # Поддержка различных голосов
        pass
```

### Маршрутизация контента
```python
class ContentRouter:
    def route_content(self, content_type, user_preferences):
        # Определение оптимального способа обработки
        # Выбор между локальными и облачными моделями
        pass
```

## Безопасность и приватность

### Локальные модели
- **Ollama** для приватной обработки текста и изображений
- **Whisper** для локального распознавания речи

### Шифрование данных
- Шифрование файлов в хранилище
- Безопасная передача данных
- Анонимизация логов

### Контроль пользователя
- Выбор уровня приватности
- Управление данными
- Возможность удаления истории

## Мониторинг и логгирование

### Мониторинг
- **Базовые метрики**: количество запросов, время ответа
- **Модели**: использование локальных vs облачных
- **Форматы**: статистика по типам контента
- **Производительность**: загрузка системы

### Логгирование
- **ERROR** - ошибки моделей, критические сбои
- **WARNING** - таймауты, fallback ответы
- **INFO** - основные события, использование моделей
- **DEBUG** - детальная отладка (только в разработке)

## Сценарии работы

### Основные команды
- **`/start`** - приветствие и настройка предпочтений
- **`/help`** - справка по возможностям
- **`/settings`** - настройка приватности и форматов
- **`/status`** - проверка работоспособности
- **`/clear`** - очистка истории диалога

### Обработка контента
- **Текстовые сообщения**: классические консультации
- **Фотографии**: анализ изображений
- **Аудио сообщения**: распознавание речи
- **Смешанный контент**: комбинированная обработка

### Форматы ответов
- **Текст**: структурированные ответы
- **Изображения**: визуализация концепций
- **Аудио**: голосовые консультации
- **Гибрид**: комбинация по запросу

## Деплой

### Окружения

#### Локальная разработка
- **Быстрый старт**: `make setup` → `make run`
- **Запуск**: `make run` или `uv run python main.py`
- **Управление**: ручной старт/стоп
- **Конфигурация**: `.env` файл
- **Установка зависимостей**: `make dev` или `uv sync`
- **Docker**: `make docker-run` или `docker-compose up`

#### Продакшн (Railway)
- **Контейнеризация**: Docker с поддержкой GPU
- **Автозапуск**: systemd внутри контейнера
- **CI/CD**: GitHub Actions
- **Мониторинг**: через Railway dashboard

### Файлы деплоя
- **`Dockerfile`** - образ для продакшена
- **`docker-compose.yml`** - локальная разработка
- **`.github/workflows/deploy.yml`** - автоматический деплой
- **`railway.toml`** - конфигурация Railway платформы

## Конфигурирование

### Переменные окружения

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Локальные модели (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_TEXT=llama3.2:3b
OLLAMA_MODEL_VISION=llava:7b

# Облачные модели (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL_TEXT=openai/gpt-4o-mini
OPENROUTER_MODEL_VISION=openai/gpt-4o

# База данных
DATABASE_URL=sqlite:///bot_data.db
REDIS_URL=redis://localhost:6379

# Приватность
DEFAULT_PRIVACY_LEVEL=local
ENABLE_CLOUD_FALLBACK=true

# Логгирование
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Опционально
DEBUG=false
```

### Файлы конфигурации
- **`.env`** - локальные переменные (не в git)
- **`env.example`** - пример конфигурации
- **`config/settings.py`** - загрузка и валидация настроек

## Управление зависимостями

### Инструмент: uv

Используем современный менеджер пакетов `uv` для управления зависимостями.

### Структура конфигурации

**pyproject.toml**:
```toml
[project]
name = "multimodal-ai-bot"
version = "0.1.0"
description = "Мультимодальный ИИ-консультант для Telegram"
dependencies = [
    "aiogram>=3.7.0",
    "aiohttp>=3.9.5",
    "python-dotenv>=1.0.1",
    "pillow>=10.0.0",
    "opencv-python>=4.8.0",
    "speechrecognition>=3.10.0",
    
    "openai-whisper>=20231117",
    "sqlalchemy>=2.0.0",
    "redis>=5.0.0",
]

[project.optional-dependencies]
dev = [
    "black>=24.4.2",
    "flake8>=7.0.0",
    "mypy>=1.10.0",
    "pytest>=8.2.2",
    "pytest-asyncio>=0.23.7",
]

local-models = [
    "ollama>=0.1.0",
    "diffusers>=0.24.0",
    "transformers>=4.35.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Основные команды

```bash
# Установка зависимостей
uv sync                    # Базовые зависимости
uv sync --extra local-models  # С локальными моделями

# Запуск приложения
uv run python main.py

# Управление моделями
ollama pull llama3.2:3b    # Загрузка текстовой модели
ollama pull llava:7b       # Загрузка мультимодальной модели
```

## Автоматизация сборок

### Makefile для проекта

```makefile
# Основные переменные
PROJECT_NAME = multimodal-ai-bot
PYTHON = uv run python
UV = uv

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help install dev run test lint format clean docker-build docker-run deploy setup-models

# Помощь (по умолчанию)
help:
	@echo "$(GREEN)Доступные команды:$(NC)"
	@echo "  $(YELLOW)install$(NC)     - Установка продакшн зависимостей"
	@echo "  $(YELLOW)dev$(NC)         - Установка всех зависимостей"
	@echo "  $(YELLOW)run$(NC)         - Запуск бота"
	@echo "  $(YELLOW)test$(NC)        - Запуск тестов"
	@echo "  $(YELLOW)lint$(NC)        - Проверка кода"
	@echo "  $(YELLOW)format$(NC)      - Форматирование кода"
	@echo "  $(YELLOW)clean$(NC)       - Очистка временных файлов"
	@echo "  $(YELLOW)setup-models$(NC) - Установка локальных моделей"
	@echo "  $(YELLOW)docker-build$(NC) - Сборка Docker образа"
	@echo "  $(YELLOW)docker-run$(NC)  - Запуск в Docker"
	@echo "  $(YELLOW)deploy$(NC)      - Деплой на Railway"

# Установка продакшн зависимостей
install:
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(UV) sync --no-dev

# Установка всех зависимостей
dev:
	@echo "$(GREEN)Установка dev зависимостей...$(NC)"
	$(UV) sync

# Запуск бота
run:
	@echo "$(GREEN)Запуск бота...$(NC)"
	$(PYTHON) main.py

# Установка локальных моделей
setup-models:
	@echo "$(GREEN)Установка локальных моделей...$(NC)"
	ollama pull llama3.2:3b
	ollama pull llava:7b
	ollama pull whisper:base

# Запуск тестов
test:
	@echo "$(GREEN)Запуск тестов...$(NC)"
	$(PYTHON) -m pytest tests/ -v

# Линтинг
lint:
	@echo "$(GREEN)Проверка кода...$(NC)"
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy .

# Форматирование
format:
	@echo "$(GREEN)Форматирование кода...$(NC)"
	$(PYTHON) -m black .

# Очистка
clean:
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Docker сборка
docker-build:
	@echo "$(GREEN)Сборка Docker образа...$(NC)"
	docker build -t $(PROJECT_NAME) .

# Docker запуск
docker-run:
	@echo "$(GREEN)Запуск в Docker...$(NC)"
	docker run --env-file .env $(PROJECT_NAME)

# Деплой
deploy:
	@echo "$(GREEN)Деплой на Railway...$(NC)"
	@echo "$(YELLOW)Убедитесь что Railway CLI установлен$(NC)"
	railway up

# Быстрая проверка проекта
check: lint test
	@echo "$(GREEN)Проект готов к коммиту!$(NC)"

# Полная подготовка dev окружения
setup: dev setup-models
	@echo "$(GREEN)Создание .env из примера...$(NC)"
	@if [ ! -f .env ]; then cp env.example .env; fi
	@echo "$(YELLOW)Не забудьте настроить .env файл!$(NC)"
```

---

*Документ служит технической отправной точкой для разработки мультимодального ИИ-консультанта с акцентом на приватность и локальную обработку данных.*
