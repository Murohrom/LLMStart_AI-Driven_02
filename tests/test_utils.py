"""Тесты для утилит проекта."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.utils.history import HistoryManager
from src.utils.validators import MessageValidator


class TestHistoryManager:
    """Тесты для класса HistoryManager."""
    
    @pytest.fixture
    def history_manager(self) -> HistoryManager:
        """Фикстура менеджера истории."""
        return HistoryManager()
    
    def test_init(self, history_manager: HistoryManager) -> None:
        """Тест инициализации менеджера истории."""
        assert history_manager.user_sessions == {}
        assert history_manager.max_messages == 20
        assert history_manager.session_ttl == 3600
    
    def test_add_message_new_user(self, history_manager: HistoryManager) -> None:
        """Тест добавления сообщения для нового пользователя."""
        user_id = "test_user"
        role = "user"
        content = "Тестовое сообщение"
        
        history_manager.add_message(user_id, role, content)
        
        assert user_id in history_manager.user_sessions
        session = history_manager.user_sessions[user_id]
        assert len(session) == 1
        assert session[0].role == role
        assert session[0].content == content
        assert session[0].timestamp is not None
    
    def test_add_message_existing_user(self, history_manager: HistoryManager) -> None:
        """Тест добавления сообщения для существующего пользователя."""
        user_id = "test_user"
        
        # Добавляем первое сообщение
        history_manager.add_message(user_id, "user", "Первое сообщение")
        
        # Добавляем второе сообщение
        history_manager.add_message(user_id, "assistant", "Ответ бота")
        
        session = history_manager.user_sessions[user_id]
        assert len(session) == 2
        assert session[0].content == "Первое сообщение"
        assert session[1].content == "Ответ бота"
    
    def test_add_message_exceeds_max_limit(self, history_manager: HistoryManager) -> None:
        """Тест что старые сообщения удаляются при превышении лимита."""
        user_id = "test_user"
        max_messages = history_manager.max_messages
        
        # Добавляем больше сообщений чем лимит
        for i in range(max_messages + 5):
            history_manager.add_message(user_id, "user", f"Сообщение {i}")
        
        session = history_manager.user_sessions[user_id]
        assert len(session) == max_messages
        
        # Проверяем что остались последние сообщения
        assert session[0].content == "Сообщение 5"
        assert session[-1].content == f"Сообщение {max_messages + 4}"
    
    def test_get_context_messages_empty(self, history_manager: HistoryManager) -> None:
        """Тест получения контекста для несуществующего пользователя."""
        result = history_manager.get_context_messages("nonexistent_user")
        assert result == []
    
    def test_get_context_messages_with_history(self, history_manager: HistoryManager) -> None:
        """Тест получения контекста с существующей историей."""
        user_id = "test_user"
        
        # Добавляем несколько сообщений
        history_manager.add_message(user_id, "user", "Вопрос 1")
        history_manager.add_message(user_id, "assistant", "Ответ 1")
        history_manager.add_message(user_id, "user", "Вопрос 2")
        
        # Получаем контекст
        context = history_manager.get_context_messages(user_id)
        
        assert len(context) == 3
        assert context[0]["role"] == "user"
        assert context[0]["content"] == "Вопрос 1"
        assert context[1]["role"] == "assistant"
        assert context[1]["content"] == "Ответ 1"
        assert context[2]["role"] == "user"
        assert context[2]["content"] == "Вопрос 2"
        
        # Проверяем что timestamp удален из контекста
        for message in context:
            assert "timestamp" not in message
    
    def test_clear_user_history_existing(self, history_manager: HistoryManager) -> None:
        """Тест очистки истории существующего пользователя."""
        user_id = "test_user"
        
        # Добавляем сообщения
        history_manager.add_message(user_id, "user", "Тест")
        assert user_id in history_manager.user_sessions
        
        # Очищаем историю
        result = history_manager.clear_user_history(user_id)
        
        assert result is True
        assert user_id not in history_manager.user_sessions
    
    def test_clear_user_history_nonexistent(self, history_manager: HistoryManager) -> None:
        """Тест очистки истории несуществующего пользователя."""
        result = history_manager.clear_user_history("nonexistent_user")
        assert result is False
    
    def test_get_user_message_count(self, history_manager: HistoryManager) -> None:
        """Тест подсчета сообщений пользователя."""
        user_id = "test_user"
        
        # Пользователь не существует
        assert history_manager.get_user_message_count(user_id) == 0
        
        # Добавляем сообщения
        history_manager.add_message(user_id, "user", "Сообщение 1")
        history_manager.add_message(user_id, "assistant", "Ответ 1")
        history_manager.add_message(user_id, "user", "Сообщение 2")
        
        assert history_manager.get_user_message_count(user_id) == 3
    
    def test_clear_old_sessions(self, history_manager: HistoryManager) -> None:
        """Тест очистки старых сессий.""" 
        from src.utils.history import DialogMessage
        
        # Создаем старую сессию
        old_time = datetime.now() - timedelta(seconds=3700)  # Старше session_ttl
        recent_time = datetime.now() - timedelta(seconds=100)  # Свежая
        
        history_manager.user_sessions = {
            "old_user": [
                DialogMessage("user", "старое сообщение", old_time)
            ],
            "recent_user": [
                DialogMessage("user", "свежее сообщение", recent_time)
            ]
        }
        
        cleared_count = history_manager.clear_old_sessions()
        
        assert cleared_count == 1
        assert "old_user" not in history_manager.user_sessions
        assert "recent_user" in history_manager.user_sessions


class TestMessageValidator:
    """Тесты для класса MessageValidator."""
    
    @pytest.fixture
    def validator(self) -> MessageValidator:
        """Фикстура валидатора сообщений."""
        return MessageValidator()
    
    def test_init(self, validator: MessageValidator) -> None:
        """Тест инициализации валидатора."""
        assert validator.MAX_MESSAGE_LENGTH == 4000
        assert validator.MIN_MESSAGE_LENGTH == 1
    
    def test_validate_user_message_valid(self, validator: MessageValidator) -> None:
        """Тест валидации корректного сообщения."""
        message = "Обычное текстовое сообщение"
        is_valid, error_type = validator.validate_user_message(message)
        
        assert is_valid is True
        assert error_type is None
    
    def test_validate_user_message_none(self, validator: MessageValidator) -> None:
        """Тест валидации None сообщения."""
        is_valid, error_type = validator.validate_user_message(None)
        
        assert is_valid is False
        assert error_type == "empty"
    
    def test_validate_user_message_empty(self, validator: MessageValidator) -> None:
        """Тест валидации пустого сообщения."""
        is_valid, error_type = validator.validate_user_message("")
        
        assert is_valid is False
        assert error_type == "empty"
    
    def test_validate_user_message_whitespace_only(self, validator: MessageValidator) -> None:
        """Тест валидации сообщения только из пробелов."""
        is_valid, error_type = validator.validate_user_message("   \n\t  ")
        
        assert is_valid is False
        assert error_type == "empty"
    
    def test_validate_user_message_too_long(self, validator: MessageValidator) -> None:
        """Тест валидации слишком длинного сообщения."""
        long_message = "x" * (validator.MAX_MESSAGE_LENGTH + 1)
        is_valid, error_type = validator.validate_user_message(long_message)
        
        assert is_valid is False
        assert error_type == "too_long"
    
    def test_validate_user_message_max_length_boundary(self, validator: MessageValidator) -> None:
        """Тест валидации сообщения близко к границе максимальной длины."""
        # Создаем разнообразное сообщение без повторений, чтобы не попасть под спам-фильтр
        boundary_message = "".join(f"слово{i} " for i in range(300))  # Примерно 2600 символов
        
        is_valid, error_type = validator.validate_user_message(boundary_message)
        
        assert is_valid is True
        assert error_type is None
    
    def test_validate_user_message_with_special_chars(self, validator: MessageValidator) -> None:
        """Тест валидации сообщения со специальными символами."""
        message = "Сообщение с эмодзи 🚀 и спецсимволами @#$%"
        is_valid, error_type = validator.validate_user_message(message)
        
        assert is_valid is True
        assert error_type is None
    
    def test_validate_user_message_multiline(self, validator: MessageValidator) -> None:
        """Тест валидации многострочного сообщения."""
        message = "Первая строка\nВторая строка\nТретья строка"
        is_valid, error_type = validator.validate_user_message(message)
        
        assert is_valid is True
        assert error_type is None
    
    def test_get_validation_error_message_empty(self, validator: MessageValidator) -> None:
        """Тест получения сообщения об ошибке для пустого текста."""
        error_message = validator.get_validation_error_message("empty")
        
        assert "🤔" in error_message
        assert "немое" in error_message.lower()
        assert "чтения мыслей" in error_message.lower()
    
    def test_get_validation_error_message_too_long(self, validator: MessageValidator) -> None:
        """Тест получения сообщения об ошибке для слишком длинного текста."""
        error_message = validator.get_validation_error_message("too_long")
        
        assert "📚" in error_message
        assert "роман" in error_message.lower()
        assert "4000" in error_message
    
    def test_get_validation_error_message_unknown(self, validator: MessageValidator) -> None:
        """Тест получения сообщения об ошибке для неизвестного типа."""
        error_message = validator.get_validation_error_message("unknown_error")
        
        assert "что-то пошло не так" in error_message.lower()
        assert "попробуй еще раз" in error_message.lower()
    
    def test_get_validation_error_message_none(self, validator: MessageValidator) -> None:
        """Тест получения сообщения об ошибке для None типа."""
        error_message = validator.get_validation_error_message(None)
        
        assert "что-то пошло не так" in error_message.lower()
        assert "попробуй еще раз" in error_message.lower()


class TestLoggerMocking:
    """Тесты для проверки что логгер корректно мокается."""
    
    def test_logger_import(self) -> None:
        """Тест что логгер импортируется без ошибок."""
        from src.utils.logger import logger
        assert logger is not None
    
    def test_logger_methods_exist(self) -> None:
        """Тест что у логгера есть необходимые методы.""" 
        from src.utils.logger import logger
        
        # Проверяем стандартные методы логгирования
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')
        
        # Проверяем кастомные методы
        assert hasattr(logger, 'log_user_message')
        assert hasattr(logger, 'log_llm_request')
        assert hasattr(logger, 'log_llm_error')
        assert hasattr(logger, 'log_validation_error')
