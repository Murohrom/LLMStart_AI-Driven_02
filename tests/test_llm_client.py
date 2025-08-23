"""Тесты для LLM клиента."""
import pytest
import asyncio
import aiohttp
from unittest.mock import patch, AsyncMock, mock_open
from src.llm.client import LLMClient


class TestLLMClient:
    """Тесты для класса LLMClient."""
    
    @pytest.fixture
    def llm_client(self, mock_settings) -> LLMClient:
        """Фикстура LLM клиента с мок настройками."""
        with patch("builtins.open", mock_open(read_data="Тестовый системный промпт")):
            return LLMClient()
    
    def test_init(self, llm_client: LLMClient, mock_settings) -> None:
        """Тест инициализации клиента."""
        assert llm_client.api_url == "https://openrouter.ai/api/v1/chat/completions"
        assert "Authorization" in llm_client.headers
        assert llm_client.headers["Authorization"].startswith("Bearer ")
        assert llm_client.headers["Content-Type"] == "application/json"
        assert llm_client.system_prompt is not None
    
    def test_load_system_prompt_success(self, mock_settings) -> None:
        """Тест успешной загрузки системного промпта."""
        test_prompt = "Специальный тестовый промпт"
        with patch("builtins.open", mock_open(read_data=test_prompt)):
            client = LLMClient()
            assert client.system_prompt == test_prompt
    
    def test_load_system_prompt_file_not_found(self, mock_settings) -> None:
        """Тест загрузки дефолтного промпта при отсутствии файла."""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            client = LLMClient()
            assert "саркастический консультант" in client.system_prompt.lower()
    
    def test_get_default_prompt(self, llm_client: LLMClient) -> None:
        """Тест получения дефолтного промпта."""
        default_prompt = llm_client._get_default_prompt()
        assert "саркастический консультант" in default_prompt.lower()
        assert "сарказм" in default_prompt.lower()
    
    def test_prepare_payload_without_context(self, llm_client: LLMClient) -> None:
        """Тест подготовки payload без контекста."""
        user_message = "Тестовое сообщение"
        payload = llm_client._prepare_payload(user_message)
        
        # Используем реальную модель из настроек
        assert "model" in payload
        assert payload["temperature"] == 0.8
        assert payload["max_tokens"] == 500
        assert len(payload["messages"]) == 2  # system + user
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"
        assert payload["messages"][1]["content"] == user_message
    
    def test_prepare_payload_with_context(self, llm_client: LLMClient) -> None:
        """Тест подготовки payload с контекстом."""
        user_message = "Новое сообщение"
        context_messages = [
            {"role": "user", "content": "Предыдущее сообщение"},
            {"role": "assistant", "content": "Предыдущий ответ"}
        ]
        
        payload = llm_client._prepare_payload(user_message, context_messages)
        
        assert len(payload["messages"]) == 4  # system + context + user
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1] == context_messages[0]
        assert payload["messages"][2] == context_messages[1] 
        assert payload["messages"][3]["role"] == "user"
        assert payload["messages"][3]["content"] == user_message
    
    def test_prepare_payload_limits_context(self, llm_client: LLMClient) -> None:
        """Тест ограничения количества сообщений в контексте."""
        user_message = "Новое сообщение"
        # Создаем 30 сообщений (больше лимита в 20)
        context_messages = []
        for i in range(30):
            context_messages.append({"role": "user", "content": f"Сообщение {i}"})
        
        payload = llm_client._prepare_payload(user_message, context_messages)
        
        # Должно быть не больше 20 сообщений: system + context (max 19) + user (1)
        assert len(payload["messages"]) == 20
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][-1]["role"] == "user"
        assert payload["messages"][-1]["content"] == user_message
    
    def test_get_max_context_messages(self, llm_client: LLMClient) -> None:
        """Тест получения максимального количества контекстных сообщений."""
        max_messages = llm_client._get_max_context_messages()
        assert max_messages == 20
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, llm_client: LLMClient, mock_aiohttp_session, mock_openrouter_response) -> None:
        """Тест успешного HTTP запроса."""
        payload = {"test": "payload"}
        
        result = await llm_client._make_request(payload)
        
        assert result == "Тестовый саркастический ответ от ИИ"
    
    @pytest.mark.asyncio 
    async def test_make_request_rate_limit_error(self, llm_client: LLMClient) -> None:
        """Тест обработки ошибки rate limit."""
        payload = {"test": "payload"}
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 429
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="Rate limit exceeded"):
                await llm_client._make_request(payload)
    
    @pytest.mark.asyncio
    async def test_make_request_auth_error(self, llm_client: LLMClient) -> None:
        """Тест обработки ошибки авторизации."""
        payload = {"test": "payload"}
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="Invalid API key"):
                await llm_client._make_request(payload)
    
    @pytest.mark.asyncio
    async def test_make_request_server_error(self, llm_client: LLMClient) -> None:
        """Тест обработки серверной ошибки."""
        payload = {"test": "payload"}
        
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text.return_value = "Internal Server Error"
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="API error 500"):
                await llm_client._make_request(payload)
    
    def test_classify_error_timeout(self, llm_client: LLMClient) -> None:
        """Тест классификации timeout ошибок."""
        error = Exception("Connection timeout occurred")
        error_type = llm_client._classify_error(error)
        assert error_type == "timeout"
    
    def test_classify_error_rate_limit(self, llm_client: LLMClient) -> None:
        """Тест классификации rate limit ошибок."""
        error = Exception("Rate limit exceeded")
        error_type = llm_client._classify_error(error)
        assert error_type == "rate_limit"
    
    def test_classify_error_auth(self, llm_client: LLMClient) -> None:
        """Тест классификации ошибок авторизации."""
        error = Exception("Invalid API key provided")
        error_type = llm_client._classify_error(error)
        assert error_type == "auth_error"
    
    def test_classify_error_network(self, llm_client: LLMClient) -> None:
        """Тест классификации сетевых ошибок."""
        error = Exception("Connection error occurred")
        error_type = llm_client._classify_error(error)
        assert error_type == "network_error"
    
    def test_classify_error_server(self, llm_client: LLMClient) -> None:
        """Тест классификации серверных ошибок."""
        error = Exception("Server error 500")
        error_type = llm_client._classify_error(error)
        assert error_type == "server_error"
    
    def test_classify_error_unknown(self, llm_client: LLMClient) -> None:
        """Тест классификации неизвестных ошибок."""
        error = Exception("Some random error")
        error_type = llm_client._classify_error(error)
        assert error_type == "unknown"
    
    def test_get_fallback_response_timeout(self, llm_client: LLMClient) -> None:
        """Тест получения fallback ответа для timeout."""
        response = llm_client._get_fallback_response("timeout")
        assert "⏰" in response or "🕒" in response or "⌛" in response
        assert any(word in response.lower() for word in ["время", "таймаут", "долго"])
    
    def test_get_fallback_response_rate_limit(self, llm_client: LLMClient) -> None:
        """Тест получения fallback ответа для rate limit."""
        response = llm_client._get_fallback_response("rate_limit")
        assert "🚦" in response or "📊" in response or "🎯" in response
        assert any(word in response.lower() for word in ["лимит", "превыс", "много"])
    
    def test_get_fallback_response_auth_error(self, llm_client: LLMClient) -> None:
        """Тест получения fallback ответа для auth error."""
        response = llm_client._get_fallback_response("auth_error")
        assert "🔑" in response or "🚪" in response
        assert any(word in response.lower() for word in ["авториз", "ключ", "пуск"])
    
    def test_get_fallback_response_unknown(self, llm_client: LLMClient) -> None:
        """Тест получения fallback ответа для неизвестной ошибки."""
        response = llm_client._get_fallback_response("unknown")
        assert len(response) > 0
        assert any(emoji in response for emoji in ["🤖", "💥", "🎭"])
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, llm_client: LLMClient, mock_aiohttp_session, mock_logger) -> None:
        """Тест успешной отправки сообщения."""
        user_message = "Тестовое сообщение"
        user_id = "test_user"
        
        result = await llm_client.send_message(user_message, None, user_id)
        
        assert result == "Тестовый саркастический ответ от ИИ"
        mock_logger.info.assert_called()
        mock_logger.log_llm_request.assert_called()
    
    @pytest.mark.asyncio
    async def test_send_message_with_context(self, llm_client: LLMClient, mock_aiohttp_session, mock_logger) -> None:
        """Тест отправки сообщения с контекстом."""
        user_message = "Новое сообщение"
        context_messages = [{"role": "user", "content": "Старое сообщение"}]
        user_id = "test_user"
        
        result = await llm_client.send_message(user_message, context_messages, user_id)
        
        assert result == "Тестовый саркастический ответ от ИИ"
        mock_logger.log_llm_request.assert_called()
    
    @pytest.mark.asyncio
    async def test_send_message_with_retry(self, llm_client: LLMClient, mock_logger) -> None:
        """Тест retry логики при ошибках."""
        user_message = "Тестовое сообщение"
        user_id = "test_user"
        
        with patch.object(llm_client, "_make_request") as mock_request:
            # Первые 2 попытки - ошибка, третья - успех
            mock_request.side_effect = [
                Exception("Network error"),
                Exception("Timeout error"), 
                "Успешный ответ"
            ]
            
            result = await llm_client.send_message(user_message, None, user_id)
            
            assert result == "Успешный ответ"
            assert mock_request.call_count == 3
            mock_logger.log_llm_error.assert_called()
    
    @pytest.mark.asyncio
    async def test_send_message_all_retries_failed(self, llm_client: LLMClient, mock_logger) -> None:
        """Тест случая когда все попытки провалились."""
        user_message = "Тестовое сообщение"
        user_id = "test_user"
        
        with patch.object(llm_client, "_make_request") as mock_request:
            mock_request.side_effect = Exception("Persistent error")
            
            result = await llm_client.send_message(user_message, None, user_id)
            
            # Должен вернуться fallback ответ
            assert len(result) > 0
            # Проверяем количество попыток - должно быть 3 (из настроек LLM_RETRY_ATTEMPTS)
            assert mock_request.call_count == 3
            mock_logger.log_llm_error.assert_called()
            mock_logger.error.assert_called()
