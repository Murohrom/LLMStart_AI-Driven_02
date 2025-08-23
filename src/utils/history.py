"""Управление историей диалогов пользователей."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.utils.logger import logger


@dataclass
class DialogMessage:
    """Структура для хранения сообщения в диалоге."""
    role: str  # "user" или "assistant"
    content: str
    timestamp: datetime


class HistoryManager:
    """Менеджер для управления историей диалогов пользователей."""
    
    def __init__(self, max_messages: int = 20, session_ttl: int = 3600):
        """
        Инициализация менеджера истории.
        
        Args:
            max_messages: Максимальное количество сообщений в контексте
            session_ttl: Время жизни сессии в секундах (по умолчанию 1 час)
        """
        self.user_sessions: Dict[str, List[DialogMessage]] = {}
        self.max_messages = max_messages
        self.session_ttl = session_ttl
        logger.info(f"HistoryManager initialized: max_messages={max_messages}, session_ttl={session_ttl}")
    
    def add_message(self, user_id: str, role: str, content: str) -> None:
        """
        Добавить сообщение в историю пользователя.
        
        Args:
            user_id: ID пользователя
            role: Роль отправителя ("user" или "assistant")
            content: Содержимое сообщения
        """
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
            logger.info(f"Created new session for user {user_id}")
        
        message = DialogMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        self.user_sessions[user_id].append(message)
        
        # Ограничиваем количество сообщений в истории
        if len(self.user_sessions[user_id]) > self.max_messages:
            removed_count = len(self.user_sessions[user_id]) - self.max_messages
            self.user_sessions[user_id] = self.user_sessions[user_id][-self.max_messages:]
            logger.debug(f"Trimmed {removed_count} old messages for user {user_id}")
        
        logger.debug(f"Added {role} message to user {user_id} history (total: {len(self.user_sessions[user_id])})")
    
    def get_context_messages(self, user_id: str) -> List[Dict[str, str]]:
        """
        Получить последние сообщения пользователя для LLM контекста.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список сообщений в формате OpenAI API
        """
        if user_id not in self.user_sessions:
            logger.debug(f"No history found for user {user_id}")
            return []
        
        messages = []
        for msg in self.user_sessions[user_id]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        logger.debug(f"Retrieved {len(messages)} context messages for user {user_id}")
        return messages
    
    def clear_user_history(self, user_id: str) -> bool:
        """
        Очистить историю конкретного пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если история была очищена, False если истории не было
        """
        if user_id in self.user_sessions:
            messages_count = len(self.user_sessions[user_id])
            del self.user_sessions[user_id]
            logger.info(f"Cleared history for user {user_id} ({messages_count} messages)")
            return True
        else:
            logger.debug(f"No history to clear for user {user_id}")
            return False
    
    def clear_old_sessions(self) -> int:
        """
        Очистить старые неактивные сессии.
        
        Returns:
            Количество удаленных сессий
        """
        cutoff_time = datetime.now() - timedelta(seconds=self.session_ttl)
        users_to_remove = []
        
        for user_id, messages in self.user_sessions.items():
            if not messages:
                users_to_remove.append(user_id)
                continue
            
            # Проверяем время последнего сообщения
            last_message_time = max(msg.timestamp for msg in messages)
            if last_message_time < cutoff_time:
                users_to_remove.append(user_id)
        
        # Удаляем старые сессии
        for user_id in users_to_remove:
            del self.user_sessions[user_id]
        
        if users_to_remove:
            logger.info(f"Cleared {len(users_to_remove)} old sessions")
        
        return len(users_to_remove)
    
    def get_session_count(self) -> int:
        """Получить количество активных сессий."""
        return len(self.user_sessions)
    
    def get_user_message_count(self, user_id: str) -> int:
        """Получить количество сообщений в истории пользователя."""
        if user_id not in self.user_sessions:
            return 0
        return len(self.user_sessions[user_id])


# Глобальный экземпляр менеджера истории
history_manager = HistoryManager()
