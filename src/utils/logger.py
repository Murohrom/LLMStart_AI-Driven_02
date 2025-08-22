"""Настройка логирования."""
import logging
import os
from typing import Optional
from src.config.settings import settings


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Настройка и возврат логгера."""
    logger = logging.getLogger(name or __name__)
    
    # Избегаем дублирования handlers
    if logger.hasHandlers():
        return logger
    
    # Настройка уровня логирования
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый handler
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    file_handler = logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Глобальный логгер для приложения
logger = setup_logger("sarcastic_bot")
