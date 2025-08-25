.PHONY: help install dev test build clean deploy cloud-deploy

# Переменные
PYTHON = python
UV = uv
DOCKER_IMAGE = sarcastic-bot
DOCKER_TAG = latest

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)Саркастический Telegram-бот - Команды управления$(NC)"
	@echo ""
	@echo "$(YELLOW)Основные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)📦 Установка зависимостей...$(NC)"
	$(UV) sync
	@echo "$(GREEN)✅ Зависимости установлены$(NC)"

dev: ## Запустить в режиме разработки
	@echo "$(GREEN)🚀 Запуск в режиме разработки...$(NC)"
	$(UV) run python src/main.py

test: ## Запустить тесты
	@echo "$(GREEN)🧪 Запуск тестов...$(NC)"
	$(UV) run pytest tests/ -v --cov=src --cov-report=term-missing

test-short: ## Запустить тесты быстро
	@echo "$(GREEN)⚡ Быстрые тесты...$(NC)"
	$(UV) run pytest tests/ -x --tb=short

build: ## Собрать Docker образ
	@echo "$(GREEN)🐳 Сборка Docker образа...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✅ Образ собран: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

run: ## Запустить в Docker
	@echo "$(GREEN)🚀 Запуск в Docker...$(NC)"
	docker run --env-file .env --rm $(DOCKER_IMAGE):$(DOCKER_TAG)

clean: ## Очистить временные файлы
	@echo "$(GREEN)🧹 Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	docker system prune -f
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

deploy: ## Локальный деплой
	@echo "$(GREEN)🚀 Локальный деплой...$(NC)"
	@make test
	@make build
	@make run

cloud-deploy: ## Подготовка к облачному деплою
	@echo "$(GREEN)☁️ Подготовка к облачному деплою...$(NC)"
	@make test
	@make build
	@echo "$(GREEN)✅ Готово к деплою в облако$(NC)"
	@echo "$(YELLOW)📖 Инструкция: DEPLOY.md$(NC)"

docker-test: ## Тестирование Docker образа
	@echo "$(GREEN)🔍 Тестирование Docker образа...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Файл .env не найден$(NC)"; \
		exit 1; \
	fi
	docker run --env-file .env --rm $(DOCKER_IMAGE):$(DOCKER_TAG) --help > /dev/null 2>&1
	@echo "$(GREEN)✅ Docker образ работает корректно$(NC)"

logs: ## Просмотр логов
	@echo "$(GREEN)📋 Логи приложения...$(NC)"
	@if [ -f logs/app.log ]; then \
		tail -f logs/app.log; \
	else \
		echo "$(YELLOW)Файл логов не найден$(NC)"; \
	fi

status: ## Статус проекта
	@echo "$(GREEN)📊 Статус проекта...$(NC)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "UV: $(shell $(UV) --version)"
	@echo "Docker: $(shell docker --version)"
	@echo "Тесты: $(shell $(UV) run pytest tests/ --tb=no -q | tail -1)"

# Команды для Windows
install.cmd: install
dev.cmd: dev
test.cmd: test
build.cmd: build
clean.cmd: clean
deploy.cmd: deploy
