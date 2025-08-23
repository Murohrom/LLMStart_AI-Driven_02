"""Общие фикстуры для тестов."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Generator

# Тестовые данные
TEST_USER_ID = "12345"
TEST_CHAT_ID = "67890"
TEST_MESSAGE_TEXT = "Тестовое сообщение"

# Мок ответа от OpenRouter API
MOCK_LLM_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": "Тестовый саркастический ответ от ИИ"
            }
        }
    ]
}

@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Фикстура для управления event loop в асинхронных тестах."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()

@pytest.fixture
def mock_settings() -> Generator[Dict[str, Any], None, None]:
    """Мок настроек приложения."""
    settings_data = {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "OPENROUTER_API_KEY": "test_api_key", 
        "OPENROUTER_MODEL": "test/model",
        "LLM_TIMEOUT": 5,
        "LLM_TEMPERATURE": 0.8,
        "LLM_RETRY_ATTEMPTS": 2,
        "LOG_LEVEL": "INFO",
        "LOG_FILE": "logs/test.log",
        "DEBUG": False
    }
    
    with patch("src.config.settings.settings") as mock:
        # Настраиваем атрибуты мока
        for key, value in settings_data.items():
            setattr(mock, key, value)
        yield mock

@pytest.fixture
def mock_telegram_message() -> MagicMock:
    """Мок Telegram сообщения."""
    message = MagicMock()
    message.from_user.id = int(TEST_USER_ID)
    message.chat.id = int(TEST_CHAT_ID)
    message.text = TEST_MESSAGE_TEXT
    message.answer = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    return message

@pytest.fixture
def mock_openrouter_response() -> Dict[str, Any]:
    """Мок ответа от OpenRouter API."""
    return MOCK_LLM_RESPONSE.copy()

@pytest.fixture
def mock_aiohttp_session() -> Generator[AsyncMock, None, None]:
    """Мок aiohttp сессии."""
    session_mock = AsyncMock()
    response_mock = AsyncMock()
    response_mock.status = 200
    response_mock.json = AsyncMock(return_value=MOCK_LLM_RESPONSE)
    
    # Правильно настраиваем async context manager
    session_mock.__aenter__ = AsyncMock(return_value=session_mock)
    session_mock.__aexit__ = AsyncMock(return_value=None)
    session_mock.post.return_value.__aenter__ = AsyncMock(return_value=response_mock)
    session_mock.post.return_value.__aexit__ = AsyncMock(return_value=None)
    
    with patch("aiohttp.ClientSession", return_value=session_mock):
        yield session_mock

@pytest.fixture
def mock_system_prompt() -> str:
    """Тестовый системный промпт."""
    return "Тестовый системный промпт для саркастического бота."

@pytest.fixture 
def mock_history_manager() -> Generator[MagicMock, None, None]:
    """Мок менеджера истории диалогов."""
    manager = MagicMock()
    manager.get_context_messages.return_value = []
    manager.add_message.return_value = None
    manager.clear_user_history.return_value = True
    manager.get_user_message_count.return_value = 0
    manager.clear_old_sessions.return_value = 0
    manager.user_sessions = {}
    
    with patch("src.utils.history.history_manager", manager):
        yield manager

@pytest.fixture
def mock_logger() -> Generator[MagicMock, None, None]:
    """Мок логгера."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock() 
    logger.warning = MagicMock()
    logger.debug = MagicMock()
    logger.log_user_message = MagicMock()
    logger.log_llm_request = MagicMock()
    logger.log_llm_error = MagicMock()
    logger.log_validation_error = MagicMock()
    
    with patch("src.utils.logger.logger", logger):
        yield logger

@pytest.fixture
def mock_validator() -> Generator[MagicMock, None, None]:
    """Мок валидатора сообщений."""
    validator = MagicMock()
    validator.validate_user_message.return_value = (True, None)
    validator.get_validation_error_message.return_value = "Ошибка валидации"
    
    with patch("src.utils.validators.validator", validator):
        yield validator
