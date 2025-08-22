"""Точка входа приложения."""
import asyncio
import sys
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
