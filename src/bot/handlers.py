"""Обработчики сообщений Telegram бота."""
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from src.config.settings import settings
from src.utils.logger import logger


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
        self.dp.message.register(self.echo_handler)
    
    async def start_handler(self, message: Message) -> None:
        """Обработчик команды /start."""
        logger.info(f"User {message.from_user.id} started bot")
        
        welcome_text = (
            "🤖 Привет! Я саркастический консультант.\n\n"
            "Расскажи мне о своей проблеме, и я дам тебе... "
            "«поддержку» в своем особом стиле.\n\n"
            "Команды:\n"
            "/help - справка\n"
            "/start - перезапуск"
        )
        
        await message.answer(welcome_text)
    
    async def help_handler(self, message: Message) -> None:
        """Обработчик команды /help."""
        logger.info(f"User {message.from_user.id} requested help")
        
        help_text = (
            "📖 Справка по боту:\n\n"
            "Я - саркастический консультант. Просто напиши мне "
            "свою проблему, и я отвечу в своем неподражаемом стиле.\n\n"
            "Доступные команды:\n"
            "/start - начать заново\n"
            "/help - показать эту справку"
        )
        
        await message.answer(help_text)
    
    async def echo_handler(self, message: Message) -> None:
        """Обработчик текстовых сообщений (эхо-режим для MVP)."""
        user_id = message.from_user.id
        user_text = message.text
        
        logger.info(f"User {user_id} sent message: {user_text}")
        
        # Простой саркастический ответ для MVP
        echo_response = (
            f"Ого, какая глубокая мысль: \"{user_text}\"\n\n"
            "Я уверен, что мир изменится от этого откровения! "
            "Пока что я простой эхо-бот, но скоро стану настоящим "
            "мастером саркастических советов. 😏"
        )
        
        await message.answer(echo_response)
        logger.info(f"Sent echo response to user {user_id}")


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
