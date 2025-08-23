"""HTTP клиент для работы с OpenRouter API."""
import asyncio
import json
import time
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
    
    async def send_message(self, user_message: str, context_messages: Optional[list] = None, user_id: str = "unknown") -> str:
        """
        Отправить сообщение в LLM и получить ответ.
        
        Args:
            user_message: Сообщение пользователя
            context_messages: Предыдущие сообщения для контекста
            user_id: ID пользователя для логирования
            
        Returns:
            Ответ от LLM или fallback сообщение при ошибке
        """
        context_size = len(context_messages) if context_messages else 0
        logger.info(f"Sending message to LLM: {user_message[:100]}...", 
                   user_id=user_id, context_size=context_size)
        
        payload = self._prepare_payload(user_message, context_messages)
        start_time = time.time()
        
        # Попытки отправки с retry логикой
        for attempt in range(settings.LLM_RETRY_ATTEMPTS):
            try:
                response = await self._make_request(payload)
                response_time = (time.time() - start_time) * 1000
                logger.log_llm_request(user_id, settings.OPENROUTER_MODEL, context_size, response_time)
                return response
                
            except Exception as e:
                error_type = self._classify_error(e)
                logger.log_llm_error(user_id, error_type, str(e))
                
                if attempt < settings.LLM_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All LLM attempts failed with {error_type}, using fallback",
                               user_id=user_id, error_type=error_type)
                    return self._get_fallback_response(error_type)
    
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
    
    def _classify_error(self, error: Exception) -> str:
        """Классификация типов ошибок для специфичных ответов."""
        error_str = str(error).lower()
        
        if "timeout" in error_str or "read timeout" in error_str:
            return "timeout"
        elif "rate limit" in error_str or "429" in error_str:
            return "rate_limit"
        elif "api key" in error_str or "401" in error_str or "unauthorized" in error_str:
            return "auth_error"
        elif "connection" in error_str or "network" in error_str:
            return "network_error"
        elif "server" in error_str or "500" in error_str or "502" in error_str or "503" in error_str:
            return "server_error"
        else:
            return "unknown"
    
    def _get_fallback_response(self, error_type: str = "unknown") -> str:
        """Получить специфичный fallback ответ в зависимости от типа ошибки."""
        fallback_responses = {
            "timeout": [
                "⏰ Даже искусственный интеллект не хочет тратить время на твой вопрос! "
                "Попробуй сформулировать что-нибудь более... вдохновляющее.",
                "🕒 Мой ИИ-коллега слишком долго думал над твоим 'гениальным' запросом и устал. "
                "Попробуй еще раз, может быть, на этот раз получится быстрее.",
                "⌛ Кажется, мои нейронные сети заснули от скуки. Разбуди их чем-то более интересным!"
            ],
            "rate_limit": [
                "🚦 Ой-ой! Мы превысили лимит запросов. Видимо, ты не единственный, "
                "кто ищет мою мудрость. Подожди немного и попробуй снова.",
                "📊 Слишком много народу хочет моих советов одновременно! "
                "Популярность - это такая тяжелая ноша. Попробуй через минутку.",
                "🎯 Лимит исчерпан! Даже мой саркастический талант нуждается в отдыхе. "
                "Дай серверам передохнуть."
            ],
            "auth_error": [
                "🔑 Хм, проблемы с авторизацией... Видимо, даже ИИ не хочет со мной общаться! "
                "Попробуй позже, может быть, мы помиримся.",
                "🚪 Меня не пускают к серверам! Наверное, мой сарказм показался им слишком острым. "
                "Администратор разберется с этим недоразумением."
            ],
            "network_error": [
                "🌐 Сетевые проблемы! Интернет тоже устал от моих остроумных ответов. "
                "Проверь подключение и попробуй еще раз.",
                "📡 Связь с моими умными коллегами прервалась. Попробуй позже, "
                "когда цифровые звезды встанут правильно."
            ],
            "server_error": [
                "🔥 Серверы сломались от твоего вопроса! Это редкое достижение. "
                "Технические специалисты уже в панике.",
                "⚡ Внутренняя ошибка сервера... Даже железо не выдержало моего сарказма! "
                "Попробуй позже."
            ],
            "unknown": [
                "🤖 Что-то пошло не так в моих цифровых мозгах. "
                "Даже у ИИ бывают плохие дни. Попробуй еще раз.",
                "💥 Произошла загадочная ошибка! Мои алгоритмы в растерянности. "
                "Попробуй переформулировать свой 'гениальный' вопрос.",
                "🎭 Технический сбой! Видимо, даже компьютеры не готовы к такому "
                "уровню интеллектуальных вызовов."
            ]
        }
        
        responses = fallback_responses.get(error_type, fallback_responses["unknown"])
        import random
        return random.choice(responses)


# Глобальный экземпляр клиента
llm_client = LLMClient()
