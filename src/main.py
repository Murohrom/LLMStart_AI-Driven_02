"""Точка входа приложения."""
import asyncio
import sys
import os

# Добавляем корневую папку в path для корректных импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot.handlers import main
from src.utils.logger import logger


if __name__ == "__main__":
    try:
        logger.info("=" * 50)
        logger.info("Sarcastic Bot Starting...")
        logger.info("=" * 50)
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)
