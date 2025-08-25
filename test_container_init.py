#!/usr/bin/env python3
"""Скрипт для тестирования инициализации контейнера без запуска бота."""

import sys
import os

# Добавляем корневую папку в path для корректных импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_container_initialization():
    """Тестирует инициализацию всех компонентов приложения."""
    try:
        print("🧪 Testing container initialization...")
        
        # Тест 1: Импорт настроек
        print("📋 Testing settings import...")
        from src.config.settings import settings
        print(f"✅ Settings loaded: TELEGRAM_BOT_TOKEN={settings.TELEGRAM_BOT_TOKEN[:10]}...")
        print(f"✅ Settings loaded: OPENROUTER_API_KEY={settings.OPENROUTER_API_KEY[:10]}...")
        
        # Тест 2: Импорт логгера
        print("📝 Testing logger import...")
        from src.utils.logger import logger
        print(f"✅ Logger initialized: {logger}")
        
        # Тест 3: Импорт менеджера истории
        print("📚 Testing history manager import...")
        from src.utils.history import history_manager
        print(f"✅ History manager initialized: {history_manager}")
        
        # Тест 4: Импорт валидатора
        print("✅ Testing validator import...")
        from src.utils.validators import validator
        print(f"✅ Validator initialized: {validator}")
        
        # Тест 5: Импорт LLM клиента
        print("🤖 Testing LLM client import...")
        from src.llm.client import llm_client
        print(f"✅ LLM client initialized: {llm_client}")
        
        # Тест 6: Загрузка системного промпта
        print("📖 Testing system prompt loading...")
        system_prompt = llm_client._load_system_prompt()
        print(f"✅ System prompt loaded: {len(system_prompt)} characters")
        
        print("🎉 All container initialization tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Container initialization test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_container_initialization()
    sys.exit(0 if success else 1)
