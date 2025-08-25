"""Тесты для обработчиков Telegram бота."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.bot.handlers import BotHandlers


class TestBotHandlers:
    """Тесты для класса BotHandlers."""
    
    @pytest.fixture
    def mock_bot(self) -> MagicMock:
        """Мок Telegram бота."""
        bot = MagicMock()
        bot.send_chat_action = AsyncMock()
        return bot
    
    @pytest.fixture
    def mock_dispatcher(self) -> MagicMock:
        """Мок диспетчера."""
        dp = MagicMock()
        dp.message.register = MagicMock()
        return dp
    
    @pytest.fixture
    def bot_handlers(self, mock_bot, mock_dispatcher, mock_settings) -> BotHandlers:
        """Фикстура обработчиков бота."""
        return BotHandlers(mock_bot, mock_dispatcher)
    
    def test_init_registers_handlers(self, mock_bot, mock_dispatcher, mock_settings) -> None:
        """Тест что все обработчики регистрируются при инициализации."""
        BotHandlers(mock_bot, mock_dispatcher)
        
        # Проверяем что register вызывался несколько раз для разных обработчиков
        assert mock_dispatcher.message.register.call_count >= 4
    
    @pytest.mark.asyncio
    async def test_start_handler(self, bot_handlers: BotHandlers, mock_telegram_message, mock_logger) -> None:
        """Тест обработчика команды /start."""
        # Патчим глобальный логгер
        with patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.start_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once()
        
        # Проверяем содержание ответа
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "🎭" in call_args
        assert "добро пожаловать" in call_args.lower()
        assert "/help" in call_args
        assert "/clear" in call_args
        
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_help_handler(self, bot_handlers: BotHandlers, mock_telegram_message, mock_logger) -> None:
        """Тест обработчика команды /help."""
        # Патчим глобальный логгер
        with patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.help_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once()
        
        # Проверяем содержание справки
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "📚" in call_args
        assert "руководство" in call_args.lower()
        assert "/start" in call_args
        assert "/clear" in call_args
        assert "/status" in call_args
        
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_clear_handler_with_history(self, bot_handlers: BotHandlers, mock_telegram_message, mock_history_manager, mock_logger) -> None:
        """Тест очистки истории когда есть что очищать."""
        mock_history_manager.clear_user_history.return_value = True
        
        # Патчим глобальные компоненты
        with patch("src.bot.handlers.history_manager", mock_history_manager), \
             patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.clear_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once()
        mock_history_manager.clear_user_history.assert_called_once()
        
        # Проверяем ответ об успешной очистке
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "🧹" in call_args
        assert "очищена" in call_args.lower()
        
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_clear_handler_no_history(self, bot_handlers: BotHandlers, mock_telegram_message, mock_history_manager, mock_logger) -> None:
        """Тест очистки истории когда нечего очищать."""
        mock_history_manager.clear_user_history.return_value = False
        
        # Патчим глобальные компоненты
        with patch("src.bot.handlers.history_manager", mock_history_manager), \
             patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.clear_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once()
        
        # Проверяем ответ о том что нечего очищать
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "🤔" in call_args
        assert "нечего" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_status_handler_success(self, bot_handlers: BotHandlers, mock_telegram_message, mock_logger) -> None:
        """Тест успешной проверки статуса."""
        # Мокаем _get_system_status метод
        mock_status = {
            'bot_status': '✅ **Бот:** Работает идеально',
            'llm_status': '✅ **LLM API:** Готов к саркастическим ответам',
            'memory_status': '💾 **Память:** 0 активных диалогов',
            'system_status': '🖥️ **Система:** CPU 10.0%, RAM 50.0%',
            'stats': '⚡ Время ответа: 100мс'
        }
        
        with patch.object(bot_handlers, '_get_system_status', return_value=mock_status), \
             patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.status_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once()
        
        # Проверяем что используется Markdown режим
        call_kwargs = mock_telegram_message.answer.call_args[1]
        assert call_kwargs.get('parse_mode') == 'Markdown'
        
        # Проверяем содержание статуса
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "🏥" in call_args
        assert "диагностика" in call_args.lower()
        assert "✅" in call_args
        
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_status_handler_error(self, bot_handlers: BotHandlers, mock_telegram_message, mock_logger) -> None:
        """Тест обработки ошибки при проверке статуса."""
        with patch.object(bot_handlers, '_get_system_status', side_effect=Exception("Test error")), \
             patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.status_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once()
        
        # Проверяем сообщение об ошибке
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "🚨" in call_args
        assert "сломалась" in call_args.lower()
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, bot_handlers: BotHandlers, mock_history_manager) -> None:
        """Тест получения статуса системы."""
        mock_history_manager.user_sessions = {"user1": {"messages": [1, 2, 3]}}
        
        with patch("src.bot.handlers.llm_client") as mock_llm_client, \
             patch("src.bot.handlers.history_manager", mock_history_manager):
            mock_llm_client.send_message.return_value = "test response"
            
            with patch("psutil.cpu_percent", return_value=15.5):
                with patch("psutil.virtual_memory") as mock_memory:
                    mock_memory.return_value.percent = 60.2
                    
                    status = await bot_handlers._get_system_status()
        
        assert "bot_status" in status
        assert "llm_status" in status  
        assert "memory_status" in status
        assert "system_status" in status
        assert "stats" in status
        
        # Проверяем статус бота
        assert "✅" in status['bot_status']
        assert "работает" in status['bot_status'].lower()
        
        # Проверяем память
        assert "1 активных диалогов" in status['memory_status']
        assert "3 сообщений" in status['memory_status']
    
    @pytest.mark.asyncio
    async def test_handle_media_message_photo(self, bot_handlers: BotHandlers, mock_telegram_message, mock_logger) -> None:
        """Тест обработки фото (теперь обрабатывается photo_handler)."""
        mock_telegram_message.photo = [{"file_id": "test"}]
        mock_telegram_message.video = None
        mock_telegram_message.document = None
        mock_telegram_message.audio = None
        mock_telegram_message.voice = None
        mock_telegram_message.sticker = None
        mock_telegram_message.animation = None
        
        # Патчим глобальный логгер
        with patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.photo_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once()
        
        # Проверяем что упоминается фото
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "фото" in call_args.lower()
        
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_sticker_handler(self, bot_handlers: BotHandlers, mock_telegram_message, mock_logger) -> None:
        """Тест обработчика стикеров."""
        # Настраиваем мок стикера
        mock_sticker = MagicMock()
        mock_sticker.file_id = "test_sticker_id"
        mock_sticker.emoji = "😀"
        mock_sticker.set_name = "test_sticker_set"
        mock_telegram_message.sticker = mock_sticker
        mock_telegram_message.caption = "Тестовый стикер"
        
        # Настраиваем мок файла
        mock_file_info = MagicMock()
        mock_file_info.file_path = "test_path"
        bot_handlers.bot.get_file = AsyncMock(return_value=mock_file_info)
        
        # Настраиваем мок скачивания
        mock_file_data = MagicMock()
        mock_file_data.read.return_value = b"fake_image_data"
        bot_handlers.bot.download_file = AsyncMock(return_value=mock_file_data)
        
        # Патчим image_processor
        mock_analyze = AsyncMock(return_value="Анализ стикера")
        with patch.object(bot_handlers.image_processor, 'analyze_image', mock_analyze), \
             patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.sticker_handler(mock_telegram_message)
        
        # Проверяем что бот отправил "печатает..."
        mock_telegram_message.bot.send_chat_action.assert_called_once()
        
        # Проверяем что анализ был вызван
        mock_analyze.assert_called_once()
        
        # Проверяем что ответ был отправлен
        mock_telegram_message.answer.assert_called_once_with("Анализ стикера")
        
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_sticker_handler_error(self, bot_handlers: BotHandlers, mock_telegram_message, mock_logger) -> None:
        """Тест обработки ошибки в обработчике стикеров."""
        # Настраиваем мок стикера
        mock_sticker = MagicMock()
        mock_sticker.file_id = "test_sticker_id"
        mock_telegram_message.sticker = mock_sticker
        
        # Симулируем ошибку при получении файла
        mock_telegram_message.bot.get_file.side_effect = Exception("File error")
        
        with patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.sticker_handler(mock_telegram_message)
        
        # Проверяем что отправился fallback ответ
        mock_telegram_message.answer.assert_called_once()
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "🚨" in call_args
        assert "стикер" in call_args.lower()
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_message_handler_media(self, bot_handlers: BotHandlers, mock_telegram_message) -> None:
        """Тест обработки медиа сообщений."""
        mock_telegram_message.text = None  # Нет текста
        mock_telegram_message.photo = [{"file_id": "test"}]
        
        await bot_handlers.message_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once()
        
        # Проверяем что упоминается медиафайл
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "медиафайл" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_message_handler_invalid_text(self, bot_handlers: BotHandlers, mock_telegram_message, mock_validator, mock_logger) -> None:
        """Тест обработки невалидного текста."""
        mock_validator.validate_user_message.return_value = (False, "too_long")
        mock_validator.get_validation_error_message.return_value = "Сообщение слишком длинное"
        
        # Патчим глобальные компоненты
        with patch("src.bot.handlers.validator", mock_validator), \
             patch("src.bot.handlers.logger", mock_logger):
            await bot_handlers.message_handler(mock_telegram_message)
        
        mock_telegram_message.answer.assert_called_once_with("Сообщение слишком длинное")
        mock_validator.validate_user_message.assert_called_once()
        mock_logger.log_validation_error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_message_handler_success(self, bot_handlers: BotHandlers, mock_telegram_message, mock_history_manager, mock_validator, mock_logger) -> None:
        """Тест успешной обработки текстового сообщения."""
        mock_validator.validate_user_message.return_value = (True, None)
        mock_history_manager.get_context_messages.return_value = []
        mock_history_manager.get_user_message_count.return_value = 1
        
        # Патчим глобальные компоненты
        with patch("src.bot.handlers.llm_client") as mock_llm_client, \
             patch("src.bot.handlers.history_manager", mock_history_manager), \
             patch("src.bot.handlers.validator", mock_validator), \
             patch("src.bot.handlers.logger", mock_logger):
            # Используем AsyncMock для асинхронного метода
            mock_llm_client.send_message = AsyncMock(return_value="Саркастический ответ")
            
            await bot_handlers.message_handler(mock_telegram_message)
        
        # Проверяем что бот отправил "печатает..."
        mock_telegram_message.bot.send_chat_action.assert_called_once()
        
        # Проверяем работу с историей
        mock_history_manager.get_context_messages.assert_called_once()
        # Проверяем что add_message вызывался для пользователя и ассистента
        assert mock_history_manager.add_message.call_count == 2  # user + assistant
        
        # Проверяем вызов LLM
        mock_llm_client.send_message.assert_called_once()
        
        # Проверяем отправку ответа
        mock_telegram_message.answer.assert_called_once_with("Саркастический ответ")
        
        mock_logger.log_user_message.assert_called_once()
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_message_handler_llm_error(self, bot_handlers: BotHandlers, mock_telegram_message, mock_history_manager, mock_validator, mock_logger) -> None:
        """Тест обработки ошибки LLM."""
        mock_validator.validate_user_message.return_value = (True, None)
        mock_history_manager.get_context_messages.return_value = []
        
        # Патчим глобальные компоненты
        with patch("src.bot.handlers.llm_client") as mock_llm_client, \
             patch("src.bot.handlers.history_manager", mock_history_manager), \
             patch("src.bot.handlers.validator", mock_validator), \
             patch("src.bot.handlers.logger", mock_logger):
            mock_llm_client.send_message.side_effect = Exception("LLM error")
            
            await bot_handlers.message_handler(mock_telegram_message)
        
        # Проверяем что отправился fallback ответ
        mock_telegram_message.answer.assert_called_once()
        call_args = mock_telegram_message.answer.call_args[0][0]
        assert "🚨" in call_args
        assert "сломать" in call_args.lower()
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_message_handler_session_cleanup(self, bot_handlers: BotHandlers, mock_telegram_message, mock_history_manager, mock_validator, mock_logger) -> None:
        """Тест периодической очистки сессий."""
        mock_validator.validate_user_message.return_value = (True, None)
        mock_history_manager.get_context_messages.return_value = []
        mock_history_manager.clear_old_sessions.return_value = 5
        
        # Симулируем что у нас есть ровно 10 пользователей (кратно 10)
        # Это должно вызвать очистку сессий
        mock_history_manager.user_sessions = {f"user_{i}": {} for i in range(10)}
        
        # Патчим глобальные компоненты
        with patch("src.bot.handlers.llm_client") as mock_llm_client, \
             patch("src.bot.handlers.history_manager", mock_history_manager), \
             patch("src.bot.handlers.validator", mock_validator), \
             patch("src.bot.handlers.logger", mock_logger):
            # Используем AsyncMock для асинхронного метода
            mock_llm_client.send_message = AsyncMock(return_value="Response")
            
            await bot_handlers.message_handler(mock_telegram_message)
        
        # Проверяем что была вызвана очистка
        # Условие: len(user_sessions) % 10 == 0, т.е. 10 % 10 == 0
        mock_history_manager.clear_old_sessions.assert_called_once()
        
        # Проверяем логирование очистки  
        mock_logger.info.assert_any_call("Cleaned 5 old sessions during maintenance")
