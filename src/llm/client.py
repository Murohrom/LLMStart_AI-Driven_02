"""HTTP клиент для работы с OpenRouter API."""
import asyncio
import json
from typing import Optional, Dict, Any
import aiohttp
from aiohttp import ClientTimeout, ClientError

from src.config.settings import settings
from src.utils.logger import logger


class LLMClient:
    """Клиент для работы с OpenRouter API."""
    
    def __init__(self) -> None:
        """Инициализация клиента."""
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/your-repo",  # Required by OpenRouter
            "X-Title": "Sarcastic Bot",  # Optional
            "Content-Type": "application/json"
        }
        self.timeout = ClientTimeout(total=settings.LLM_TIMEOUT)
        
        # Загружаем системный промпт
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Загрузка системного промпта из файла."""
        try:
            with open("prompts/system.txt", "r", encoding="utf-8") as f:
                prompt = f.read().strip()
                logger.info("System prompt loaded successfully")
                return prompt
        except FileNotFoundError:
            logger.warning("System prompt file not found, using default")
            return self._get_default_prompt()
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Получить дефолтный системный промпт."""
        return (
            "Ты - саркастический консультант. Отвечай на проблемы пользователей "
            "в вроде бы ободряющем тоне, но при этом тонко обесценивай их старания "
            "и усилия. Делай это элегантно, через скрытый сарказм и псевдо-мотивацию, "
            "которая на самом деле принижает значимость их действий."
        )
    
    async def send_message(self, user_message: str, context_messages: Optional[list] = None) -> str:
        """
        Отправить сообщение в LLM и получить ответ.
        
        Args:
            user_message: Сообщение пользователя
            context_messages: Предыдущие сообщения для контекста
            
        Returns:
            Ответ от LLM или fallback сообщение при ошибке
        """
        logger.info(f"Sending message to LLM: {user_message[:100]}...")
        context_info = f" with {len(context_messages)} context messages" if context_messages else ""
        logger.debug(f"LLM request{context_info}")
        
        payload = self._prepare_payload(user_message, context_messages)
        
        # Попытки отправки с retry логикой
        for attempt in range(settings.LLM_RETRY_ATTEMPTS):
            try:
                response = await self._make_request(payload)
                logger.info(f"LLM response received on attempt {attempt + 1}")
                return response
                
            except Exception as e:
                logger.warning(f"LLM request failed (attempt {attempt + 1}): {e}")
                
                if attempt < settings.LLM_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("All LLM attempts failed, using fallback")
                    return self._get_fallback_response()
    
    def _prepare_payload(self, user_message: str, context_messages: Optional[list] = None) -> Dict[str, Any]:
        """Подготовить payload для запроса к OpenRouter."""
        # Начинаем с системного промпта
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Добавляем контекст из истории (исключая последнее user сообщение)
        if context_messages:
            # Фильтруем контекст: берем не более 19 сообщений (20-1 для нового)
            context_to_add = context_messages[-(self._get_max_context_messages() - 1):]
            messages.extend(context_to_add)
            logger.debug(f"Added {len(context_to_add)} context messages to payload")
        
        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": user_message})
        
        return {
            "model": settings.OPENROUTER_MODEL,
            "messages": messages,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": 500
        }
    
    def _get_max_context_messages(self) -> int:
        """Получить максимальное количество сообщений в контексте."""
        return 20  # Согласно vision.md
    
    async def _make_request(self, payload: Dict[str, Any]) -> str:
        """Выполнить HTTP запрос к OpenRouter API."""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                self.api_url,
                headers=self.headers,
                json=payload
            ) as response:
                
                if response.status == 429:
                    raise Exception("Rate limit exceeded")
                elif response.status == 401:
                    raise Exception("Invalid API key")
                elif response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                
                data = await response.json()
                
                # Извлекаем ответ из JSON
                try:
                    message_content = data["choices"][0]["message"]["content"]
                    logger.info(f"LLM response: {message_content[:100]}...")
                    return message_content.strip()
                except (KeyError, IndexError) as e:
                    logger.error(f"Unexpected API response format: {data}")
                    raise Exception(f"Invalid response format: {e}")
    
    def _get_fallback_response(self) -> str:
        """Получить fallback ответ при недоступности LLM."""
        fallbacks = [
            "Даже мой сарказм сломался от твоего вопроса. Попробуй позже.",
            "Ого, ты сумел сломать даже ИИ! Это настоящее достижение. 🤖💥",
            "Кажется, мои сервера устали от твоих глубоких мыслей. Попробуй еще раз.",
            "Технические неполадки... Видимо, даже компьютеры не готовы к такому уровню 'гениальности'."
        ]
        import random
        return random.choice(fallbacks)


# Глобальный экземпляр клиента
llm_client = LLMClient()
