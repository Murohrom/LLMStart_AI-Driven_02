"""Модуль для обработки изображений."""
import base64
import io
from typing import Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageOps
import aiohttp

from src.config.settings import settings
from src.utils.logger import logger


class ImageProcessor:
    """Класс для обработки изображений."""
    
    def __init__(self) -> None:
        """Инициализация процессора изображений."""
        self.max_size = 10 * 1024 * 1024  # 10MB
        self.max_dimensions = (1024, 1024)
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}
    
    def validate_image(self, image_data: bytes) -> Tuple[bool, str]:
        """
        Валидация изображения.
        
        Args:
            image_data: Байты изображения
            
        Returns:
            Tuple[bool, str]: (валидно, сообщение об ошибке)
        """
        try:
            # Проверка размера
            if len(image_data) > self.max_size:
                return False, f"Файл слишком большой: {len(image_data) // 1024 // 1024}MB"
            
            # Проверка формата через PIL
            image = Image.open(io.BytesIO(image_data))
            format_name = image.format.lower()
            
            if format_name not in {'jpeg', 'jpg', 'png', 'webp'}:
                return False, f"Неподдерживаемый формат: {format_name}"
            
            # Проверка размеров
            width, height = image.size
            if width > 4096 or height > 4096:
                return False, f"Изображение слишком большое: {width}x{height}"
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Ошибка валидации изображения: {e}")
            return False, f"Ошибка чтения файла: {str(e)}"
    
    def optimize_image(self, image_data: bytes) -> bytes:
        """
        Оптимизация изображения.
        
        Args:
            image_data: Байты изображения
            
        Returns:
            bytes: Оптимизированные байты изображения
        """
        try:
            # Открываем изображение
            image = Image.open(io.BytesIO(image_data))
            
            # Конвертируем в RGB если нужно
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Изменяем размер если слишком большое
            max_width, max_height = self.max_dimensions
            if image.width > max_width or image.height > max_height:
                image.thumbnail(self.max_dimensions, Image.Resampling.LANCZOS)
            
            # Сохраняем в JPEG с оптимизацией
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации изображения: {e}")
            return image_data
    
    def image_to_base64(self, image_data: bytes) -> str:
        """
        Конвертация изображения в base64.
        
        Args:
            image_data: Байты изображения
            
        Returns:
            str: Base64 строка
        """
        return base64.b64encode(image_data).decode('utf-8')
    
    async def analyze_image(self, image_data: bytes, user_prompt: str = "") -> str:
        """
        Анализ изображения через OpenRouter API.
        
        Args:
            image_data: Байты изображения
            user_prompt: Дополнительный промпт пользователя
            
        Returns:
            str: Описание изображения
        """
        try:
            # Валидация
            is_valid, error_msg = self.validate_image(image_data)
            if not is_valid:
                return f"❌ Ошибка валидации: {error_msg}"
            
            # Оптимизация
            optimized_data = self.optimize_image(image_data)
            base64_image = self.image_to_base64(optimized_data)
            
            # Формируем промпт
            system_prompt = (
                "Ты - саркастичный аналитик изображений. "
                "Анализируй изображения с юмором и иронией. "
                "Давай не только описание, но и забавные комментарии. "
                "Будь остроумным, но не злым."
            )
            
            user_message = f"Проанализируй это изображение: {user_prompt}".strip()
            
            # Подготавливаем сообщения для API
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_message
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Отправляем запрос к OpenRouter
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/your-repo",
                        "X-Title": "AI-Driven Bot"
                    },
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": messages,
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        logger.info(f"Изображение проанализировано успешно")
                        return content
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка API OpenRouter: {response.status} - {error_text}")
                        return f"❌ Ошибка анализа изображения: {response.status}"
                        
        except Exception as e:
            logger.error(f"Ошибка анализа изображения: {e}")
            return f"❌ Неожиданная ошибка при анализе: {str(e)}"
    
    async def generate_image(self, prompt: str) -> Optional[bytes]:
        """
        Генерация изображения через OpenRouter API.
        
        Args:
            prompt: Промпт для генерации
            
        Returns:
            Optional[bytes]: Байты сгенерированного изображения или None
        """
        try:
            # Используем DALL-E 3 через OpenRouter
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/your-repo",
                        "X-Title": "AI-Driven Bot"
                    },
                    json={
                        "model": "openai/dall-e-3",
                        "prompt": prompt,
                        "n": 1,
                        "size": "1024x1024",
                        "quality": "standard"
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        image_url = data['data'][0]['url']
                        
                        # Скачиваем изображение
                        async with session.get(image_url) as img_response:
                            if img_response.status == 200:
                                image_data = await img_response.read()
                                logger.info(f"Изображение сгенерировано успешно")
                                return image_data
                            else:
                                logger.error(f"Ошибка скачивания изображения: {img_response.status}")
                                return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка генерации изображения: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка генерации изображения: {e}")
            return None
