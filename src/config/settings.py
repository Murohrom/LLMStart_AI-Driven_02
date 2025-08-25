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
    
    # OpenRouter LLM
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "openai/gpt-oss-20b:free"
    

    
    # LLM настройки
    LLM_TIMEOUT: int = 10
    LLM_TEMPERATURE: float = 0.8
    LLM_RETRY_ATTEMPTS: int = 3
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/bot.log"
    DEBUG: bool = False
    
    def __init__(self) -> None:
        """Инициализация настроек с валидацией."""
        self.TELEGRAM_BOT_TOKEN = self._get_required_env("TELEGRAM_BOT_TOKEN")
        self.OPENROUTER_API_KEY = self._get_required_env("OPENROUTER_API_KEY")

        
        self.OPENROUTER_MODEL = getenv("OPENROUTER_MODEL", self.OPENROUTER_MODEL)
        self.LLM_TIMEOUT = int(getenv("LLM_TIMEOUT", str(self.LLM_TIMEOUT)))
        self.LLM_TEMPERATURE = float(getenv("LLM_TEMPERATURE", str(self.LLM_TEMPERATURE)))
        self.LLM_RETRY_ATTEMPTS = int(getenv("LLM_RETRY_ATTEMPTS", str(self.LLM_RETRY_ATTEMPTS)))
        
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
