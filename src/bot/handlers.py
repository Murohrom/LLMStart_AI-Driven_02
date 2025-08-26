"""Обработчики сообщений Telegram бота."""
import asyncio
import time
import psutil
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from src.config.settings import settings
from src.utils.logger import logger
from src.llm.client import llm_client
from src.utils.history import history_manager
from src.utils.validators import validator
from src.multimodal.image_processor import ImageProcessor


class BotHandlers:
    """Класс для организации обработчиков бота."""
    
    def __init__(self, bot: Bot, dp: Dispatcher) -> None:
        """Инициализация обработчиков."""
        self.bot = bot
        self.dp = dp
        self.image_processor = ImageProcessor()
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Регистрация всех обработчиков."""
        self.dp.message.register(self.start_handler, CommandStart())
        self.dp.message.register(self.help_handler, Command("help"))
        self.dp.message.register(self.clear_handler, Command("clear"))
        self.dp.message.register(self.status_handler, Command("status"))

        self.dp.message.register(self.photo_handler, F.photo)
        self.dp.message.register(self.sticker_handler, F.sticker)
        self.dp.message.register(self.document_handler, F.document)
        self.dp.message.register(self.message_handler)
    
    async def start_handler(self, message: Message) -> None:
        """Обработчик команды /start."""
        logger.info(f"User {message.from_user.id} started bot")
        
        welcome_text = (
            "🎭 О, какая неожиданность! Еще один искатель мудрости!\n\n"
            "Добро пожаловать в мой уютный мирок псевдо-поддержки. "
            "Я здесь, чтобы помочь тебе... ну, или создать иллюзию помощи. "
            "Расскажи мне о своих 'грандиозных' планах, и я дам тебе совет, "
            "который ты точно... оценишь по достоинству.\n\n"
            "🤖 P.S. Теперь я работаю на настоящем ИИ с мультимодальными возможностями! "
            "Представляешь? Машина учит машину быть саркастичной и анализировать картинки. "
            "Прогресс не остановить!\n\n"
            "📋 Мои возможности:\n"
            "/help - подробное руководство по моему 'таланту'\n"
            "/clear - стереть память о твоих 'достижениях'\n"
            "/image <описание> - создать 'шедевр' по твоему описанию\n"
            "📸 Отправляй мне фотографии и стикеры - я их проанализирую с юмором\n"
            "/start - начать это увлекательное путешествие заново"
        )
        
        await message.answer(welcome_text)
    
    async def help_handler(self, message: Message) -> None:
        """Обработчик команды /help."""
        logger.info(f"User {message.from_user.id} requested help")
        
        help_text = (
            "📚 Руководство по взаимодействию с гением:\n\n"
            "Процесс элементарно простой: ты пишешь мне свою 'уникальную' проблему, "
            "а я отвечаю с таким энтузиазмом, что у тебя появится мотивация... "
            "или что-то очень похожее на нее.\n\n"
            "🎪 Мои профессиональные таланты:\n"
            "• Псевдо-мотивация мирового класса\n"
            "• Элегантное обесценивание усилий\n"
            "• Советы с гарантированным* подтекстом\n"
            "• Поддержка с привкусом реальности\n"
            "• Анализ изображений с сарказмом\n"
            "• Анализ 'гениальных' картинок\n\n"
            "🎭 Доступные команды:\n"
            "/start - начать это захватывающее приключение заново\n"
            "/help - перечитать этот шедевр инструкций\n"
            "/clear - стереть следы твоих 'гениальных' вопросов\n"
            "/status - проверить мое блестящее техническое состояние\n\n"
            "📸 Мультимодальные возможности:\n"
            "• Отправляй мне фотографии - я их проанализирую с юмором\n"
            "• Отправляй стикеры - я их тоже проанализирую\n"
            "• Загружай изображения как документы\n\n"
            "📝 *Гарантия распространяется исключительно на качество сарказма"
        )
        
        await message.answer(help_text)
    
    async def clear_handler(self, message: Message) -> None:
        """Обработчик команды /clear."""
        user_id = str(message.from_user.id)
        logger.info(f"User {user_id} requested history clear")
        
        # Очищаем историю пользователя
        cleared = history_manager.clear_user_history(user_id)
        
        if cleared:
            response = (
                "🧹 История диалога очищена!\n\n"
                "Теперь я забыл о всех твоих предыдущих «достижениях». "
                "Можешь начать заново и поразить меня новым уровнем гениальности!"
            )
        else:
            response = (
                "🤔 А очищать-то нечего!\n\n"
                "У тебя и так не было никакой истории. "
                "Видимо, даже память о твоих сообщениях испарилась от их... уникальности."
            )
        
        await message.answer(response)
    
    async def status_handler(self, message: Message) -> None:
        """Обработчик команды /status для проверки работоспособности."""
        user_id = str(message.from_user.id)
        logger.info(f"User {user_id} requested system status")
        
        try:
            # Получаем информацию о системе
            status_info = await self._get_system_status()
            
            # Формируем саркастический ответ со статусом
            status_message = (
                "🏥 **Диагностика моего блестящего состояния:**\n\n"
                f"{status_info['bot_status']}\n"
                f"{status_info['llm_status']}\n"
                f"{status_info['memory_status']}\n"
                f"{status_info['system_status']}\n\n"
                "📊 **Статистика величия:**\n"
                f"{status_info['stats']}\n\n"
                "🎭 Как видишь, я в отличной форме для раздачи 'мудрых' советов!"
            )
            
            await message.answer(status_message, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            error_message = (
                "🚨 Даже проверка моего статуса сломалась! "
                "Это новый уровень технических 'достижений'. "
                "Но не волнуйся, я всё еще здесь, чтобы давать тебе советы... 🤖💔"
            )
            await message.answer(error_message)
    
    async def _get_system_status(self) -> dict:
        """Получение информации о состоянии системы."""
        start_time = time.time()
        
        # Проверка бота
        bot_status = "✅ **Бот:** Работает идеально (как всегда)"
        
        # Проверка LLM API
        try:
            test_response = await asyncio.wait_for(
                llm_client.send_message("test", [], "system_check"), timeout=5
            )
            llm_status = "✅ **LLM API:** Готов к саркастическим ответам"
        except asyncio.TimeoutError:
            llm_status = "⚠️ **LLM API:** Медленно думает (как обычно)"
        except Exception:
            llm_status = "❌ **LLM API:** Временно недоступен"
        
        # Проверка памяти и истории
        session_count = len(history_manager.user_sessions)
        total_messages = sum(
            len(session.get('messages', [])) 
            for session in history_manager.user_sessions.values()
        )
        memory_status = f"💾 **Память:** {session_count} активных диалогов, {total_messages} сообщений"
        
        # Системная информация
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            
            system_status = (
                f"🖥️ **Система:** CPU {cpu_percent:.1f}%, "
                f"RAM {memory_percent:.1f}%, "
                f"Uptime {uptime.days}д {uptime.seconds//3600}ч"
            )
        except Exception:
            system_status = "🖥️ **Система:** Информация недоступна"
        
        # Статистика
        response_time = (time.time() - start_time) * 1000
        stats = (
            f"⚡ Время ответа: {response_time:.0f}мс\n"
            f"🕐 Проверено: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        return {
            'bot_status': bot_status,
            'llm_status': llm_status,
            'memory_status': memory_status,
            'system_status': system_status,
            'stats': stats
        }
    

    
    async def message_handler(self, message: Message) -> None:
        """Обработчик текстовых сообщений с интеграцией LLM и историей."""
        user_id = str(message.from_user.id)
        user_text = message.text
        
        # Обработка медиафайлов (теперь обрабатываются отдельными обработчиками)
        if not user_text:
            # Для необработанных медиафайлов
            await message.answer(
                "🎭 О, медиафайл! Как интересно... Но я специализируюсь на тексте, изображениях и стикерах. "
                "Попробуй отправить мне текст, картинку или стикер, и я с удовольствием их проанализирую с сарказмом."
            )
            return
        
        # Валидация текстового сообщения
        is_valid, error_type = validator.validate_user_message(user_text)
        if not is_valid:
            error_message = validator.get_validation_error_message(error_type)
            await message.answer(error_message)
            logger.log_validation_error(user_id, error_type, user_text[:50])
            return
        
        logger.log_user_message(user_id, user_text)
        
        try:
            # Отправляем сообщение "печатает..." для лучшего UX
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Получаем контекст из истории диалога
            context_messages = history_manager.get_context_messages(user_id)
            
            # Добавляем новое сообщение пользователя в историю
            history_manager.add_message(user_id, "user", user_text)
            
            # Получаем ответ от LLM с учетом контекста
            llm_response = await llm_client.send_message(user_text, context_messages, user_id)
            
            # Добавляем ответ бота в историю
            history_manager.add_message(user_id, "assistant", llm_response)
            
            # Отправляем ответ пользователю
            await message.answer(llm_response)
            logger.info(f"Sent LLM response to user {user_id} (history: {history_manager.get_user_message_count(user_id)} messages)")
            
            # Периодически очищаем старые сессии
            if len(history_manager.user_sessions) % 10 == 0:  # Каждые 10 новых пользователей
                cleaned = history_manager.clear_old_sessions()
                if cleaned > 0:
                    logger.info(f"Cleaned {cleaned} old sessions during maintenance")
            
        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {e}")
            
            # Fallback ответ при ошибке
            error_response = (
                "🚨 Поздравляю! Ты сумел сломать даже мой отточенный саркастический алгоритм. "
                "Это достижение достойно... особого восхищения. "
                "Дай мне минутку собрать осколки моего достоинства и попробуй еще раз. 🤖💔"
            )
            await message.answer(error_response)
    

    
    async def photo_handler(self, message: Message) -> None:
        """Обработчик фотографий."""
        user_id = str(message.from_user.id)
        logger.info(f"User {user_id} sent a photo")
        
        try:
            # Получаем фото с максимальным размером
            photo = message.photo[-1]  # Берем самое большое фото
            file_info = await self.bot.get_file(photo.file_id)
            
            # Скачиваем фото
            photo_data = await self.bot.download_file(file_info.file_path)
            image_data = photo_data.read()
            
            # Получаем подпись к фото (если есть)
            caption = message.caption or ""
            
            # Отправляем сообщение "печатает..."
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Анализируем изображение
            analysis = await self.image_processor.analyze_image(image_data, caption)
            
            # Отправляем анализ
            await message.answer(analysis)
            logger.info(f"Photo analyzed successfully for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing photo for user {user_id}: {e}")
            await message.answer(
                "🚨 Ой! Что-то пошло не так с анализом твоего фото. "
                "Возможно, оно слишком... уникальное для моего понимания."
            )
    
    async def sticker_handler(self, message: Message) -> None:
        """Обработчик стикеров."""
        user_id = str(message.from_user.id)
        logger.info(f"User {user_id} sent a sticker")
        
        try:
            # Получаем стикер
            sticker = message.sticker
            file_info = await self.bot.get_file(sticker.file_id)
            
            # Скачиваем стикер
            sticker_data = await self.bot.download_file(file_info.file_path)
            image_data = sticker_data.read()
            
            # Получаем подпись к стикеру (если есть)
            caption = message.caption or ""
            
            # Добавляем информацию о стикере к подписи
            sticker_info = f"Стикер: {sticker.emoji or 'без эмодзи'} - {sticker.set_name or 'из неизвестного набора'}"
            full_caption = f"{caption} {sticker_info}".strip()
            
            # Отправляем сообщение "печатает..."
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Анализируем изображение стикера
            analysis = await self.image_processor.analyze_image(image_data, full_caption)
            
            # Отправляем анализ
            await message.answer(analysis)
            logger.info(f"Sticker analyzed successfully for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing sticker for user {user_id}: {e}")
            await message.answer(
                "🚨 Ой! Что-то пошло не так с анализом твоего стикера. "
                "Возможно, он слишком... креативный для моего понимания."
            )
    
    async def document_handler(self, message: Message) -> None:
        """Обработчик документов (изображений)."""
        user_id = str(message.from_user.id)
        document = message.document
        
        # Проверяем, что это изображение
        if not document.mime_type or not document.mime_type.startswith('image/'):
            await message.answer(
                "📄 О, документ! Как интересно... Но я специализируюсь только на изображениях. "
                "Пришли мне картинку, и я с удовольствием её проанализирую с сарказмом."
            )
            return
        
        logger.info(f"User {user_id} sent an image document: {document.file_name}")
        
        try:
            # Скачиваем документ
            file_info = await self.bot.get_file(document.file_id)
            doc_data = await self.bot.download_file(file_info.file_path)
            image_data = doc_data.read()
            
            # Получаем подпись к документу (если есть)
            caption = message.caption or ""
            
            # Отправляем сообщение "печатает..."
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Анализируем изображение
            analysis = await self.image_processor.analyze_image(image_data, caption)
            
            # Отправляем анализ
            await message.answer(analysis)
            logger.info(f"Document image analyzed successfully for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing document image for user {user_id}: {e}")
            await message.answer(
                "🚨 Ой! Что-то пошло не так с анализом твоего документа. "
                "Возможно, он слишком... сложный для моего понимания."
            )


async def main() -> None:
    """Основная функция для запуска бота."""
    logger.info("Starting sarcastic bot...")
    
    try:
        # Создание бота и диспетчера
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        dp = Dispatcher()
        
        # Инициализация обработчиков
        BotHandlers(bot, dp)
        
        logger.info("Bot handlers registered successfully")
        
        # Запуск polling
        logger.info("Starting polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        logger.info("Bot stopped")
