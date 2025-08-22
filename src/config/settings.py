"""Настройки приложения."""
from os import getenv
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Settings:
    """Класс для управления настройками приложения."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/bot.log"
    DEBUG: bool = False
    
    def __init__(self) -> None:
        """Инициализация настроек с валидацией."""
        self.TELEGRAM_BOT_TOKEN = self._get_required_env("TELEGRAM_BOT_TOKEN")
        self.LOG_LEVEL = getenv("LOG_LEVEL", self.LOG_LEVEL)
        self.LOG_FILE = getenv("LOG_FILE", self.LOG_FILE)
        self.DEBUG = getenv("DEBUG", "false").lower() == "true"
        
    def _get_required_env(self, key: str) -> str:
        """Получить обязательную переменную окружения."""
        value = getenv(key)
        if not value:
            raise ValueError(f"Environment variable {key} is required")
        return value


# Глобальный экземпляр настроек
settings = Settings()
