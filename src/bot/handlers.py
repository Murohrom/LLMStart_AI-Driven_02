"""Обработчики сообщений Telegram бота."""
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from src.config.settings import settings
from src.utils.logger import logger
from src.llm.client import llm_client
from src.utils.history import history_manager


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
            "/clear - стереть следы твоих 'гениальных' вопросов\n\n"
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
    
    async def message_handler(self, message: Message) -> None:
        """Обработчик текстовых сообщений с интеграцией LLM и историей."""
        user_id = str(message.from_user.id)
        user_text = message.text
        
        if not user_text:
            await message.answer(
                "🤔 Интересный подход! Немое общение с ботом. "
                "К сожалению, мой талант чтения мыслей пока в разработке. "
                "Попробуй написать что-нибудь текстом - я специализируюсь именно на этом 'искусстве'."
            )
            return
        
        logger.info(f"User {user_id} sent message: {user_text[:100]}...")
        
        try:
            # Отправляем сообщение "печатает..." для лучшего UX
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # Получаем контекст из истории диалога
            context_messages = history_manager.get_context_messages(user_id)
            
            # Добавляем новое сообщение пользователя в историю
            history_manager.add_message(user_id, "user", user_text)
            
            # Получаем ответ от LLM с учетом контекста
            llm_response = await llm_client.send_message(user_text, context_messages)
            
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
