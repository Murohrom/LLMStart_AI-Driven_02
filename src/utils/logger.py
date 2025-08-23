"""Настройка логирования."""
import logging
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from src.config.settings import settings


class StructuredFormatter(logging.Formatter):
    """Структурированный форматтер для JSON логов."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Форматирование записи в JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Добавляем исключения если есть
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Добавляем extra поля если есть
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Настройка и возврат логгера."""
    logger = logging.getLogger(name or __name__)
    
    # Избегаем дублирования handlers
    if logger.hasHandlers():
        return logger
    
    # Настройка уровня логирования
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Консольный formatter (читаемый)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Файловый formatter (JSON для продакшена)
    file_formatter = StructuredFormatter() if not settings.DEBUG else console_formatter
    
    # Консольный handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Файловый handler
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    file_handler = logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


class BotLogger:
    """Обертка для логгера с дополнительным контекстом."""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
    
    def log_user_message(self, user_id: str, message: str, message_length: int = None) -> None:
        """Логирование сообщения пользователя."""
        extra = {
            "user_id": user_id,
            "message_length": message_length or len(message),
            "event_type": "user_message"
        }
        self._logger.info(f"User message: {message[:100]}...", extra=extra)
    
    def log_llm_request(self, user_id: str, model: str, context_size: int, 
                       response_time: float = None) -> None:
        """Логирование запроса к LLM."""
        extra = {
            "user_id": user_id,
            "model": model,
            "context_size": context_size,
            "response_time_ms": response_time,
            "event_type": "llm_request"
        }
        message = f"LLM request: model={model}, context={context_size}"
        if response_time:
            message += f", time={response_time:.0f}ms"
        self._logger.info(message, extra=extra)
    
    def log_llm_error(self, user_id: str, error_type: str, error_message: str) -> None:
        """Логирование ошибки LLM."""
        extra = {
            "user_id": user_id,
            "error_type": error_type,
            "event_type": "llm_error"
        }
        self._logger.error(f"LLM error: {error_type} - {error_message}", extra=extra)
    
    def log_validation_error(self, user_id: str, error_type: str, message_info: str) -> None:
        """Логирование ошибки валидации."""
        extra = {
            "user_id": user_id,
            "validation_error": error_type,
            "event_type": "validation_error"
        }
        self._logger.warning(f"Validation error: {error_type} - {message_info}", extra=extra)
    
    def info(self, message: str, **kwargs) -> None:
        """Обычное info логирование."""
        self._logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Обычное warning логирование."""
        self._logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Обычное error логирование."""
        self._logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Обычное debug логирование."""
        self._logger.debug(message, extra=kwargs)


# Глобальный логгер для приложения  
base_logger = setup_logger("sarcastic_bot")
logger = BotLogger(base_logger)
