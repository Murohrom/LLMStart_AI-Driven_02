"""Обработчики сообщений Telegram бота."""
import asyncio
import time
import psutil
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from src.config.settings import settings
from src.utils.logger import logger
from src.llm.client import llm_client
from src.utils.history import history_manager
from src.utils.validators import validator


class BotHandlers:
    """Класс для организации обработчиков бота."""
    
    def __init__(self, bot: Bot, dp: Dispatcher) -> None:
        """Инициализация обработчиков."""
        self.bot = bot
        self.dp = dp
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Регистрация всех обработчиков."""
        self.dp.message.register(self.start_handler, CommandStart())
        self.dp.message.register(self.help_handler, Command("help"))
        self.dp.message.register(self.clear_handler, Command("clear"))
        self.dp.message.register(self.status_handler, Command("status"))
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
            "🤖 P.S. Теперь я работаю на настоящем ИИ! "
            "Представляешь? Машина учит машину быть саркастичной. "
            "Прогресс не остановить!\n\n"
            "📋 Мои возможности:\n"
            "/help - подробное руководство по моему 'таланту'\n"
            "/clear - стереть память о твоих 'достижениях'\n"
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
            "• Поддержка с привкусом реальности\n\n"
            "🎭 Доступные команды:\n"
            "/start - начать это захватывающее приключение заново\n"
            "/help - перечитать этот шедевр инструкций\n"
            "/clear - стереть следы твоих 'гениальных' вопросов\n"
            "/status - проверить мое блестящее техническое состояние\n\n"
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
    
    async def _handle_media_message(self, message: Message) -> None:
        """Обработка медиафайлов с саркастическими ответами."""
        user_id = str(message.from_user.id)
        
        # Определяем тип медиа
        if message.photo:
            media_type = "фото"
        elif message.video:
            media_type = "видео"
        elif message.document:
            media_type = "документ"
        elif message.audio:
            media_type = "аудио"
        elif message.voice:
            media_type = "голосовое сообщение"
        elif message.sticker:
            media_type = "стикер"
        elif message.animation:
            media_type = "GIF"
        else:
            media_type = "медиафайл"
        
        logger.info(f"User {user_id} sent {media_type}")
        
        # Саркастические ответы на медиа
        responses = [
            f"🎨 Какой потрясающий {media_type}! К сожалению, мой талант ограничивается "
            "исключительно текстовым сарказмом. Попробуй описать словами то, "
            "что ты хотел передать этим... произведением искусства.",
            
            f"📱 О, {media_type}! Я восхищен твоей верой в то, что бот умеет "
            "анализировать визуальный контент. Увы, я специализируюсь только на "
            "письменном обесценивании твоих усилий. Напиши текстом!",
            
            f"🤖 Интересный {media_type}, но я всего лишь текстовый саркастический "
            "консультант. Мои 'выдающиеся' способности пока не распространяются "
            "на мультимедиа. Попробуй выразить свои мысли словами.",
            
            f"🎭 {media_type.capitalize()} - это конечно круто, но я умею работать только с текстом. "
            "Опиши мне свою 'гениальную' проблему словами, и я дам тебе совет, "
            "который ты точно... оценишь."
        ]
        
        import random
        response = random.choice(responses)
        await message.answer(response)
    
    async def message_handler(self, message: Message) -> None:
        """Обработчик текстовых сообщений с интеграцией LLM и историей."""
        user_id = str(message.from_user.id)
        user_text = message.text
        
        # Обработка медиафайлов
        if not user_text:
            await self._handle_media_message(message)
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
