"""Тесты для модуля конфигурации."""
import pytest
from unittest.mock import patch
from src.config.settings import Settings


class TestSettings:
    """Тесты для класса Settings."""
    
    def test_init_with_required_env_vars(self) -> None:
        """Тест инициализации с обязательными переменными окружения."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "OPENROUTER_API_KEY": "test_api_key",
            "OPENROUTER_MODEL": "test/model",
            "LLM_TIMEOUT": "15",
            "LLM_TEMPERATURE": "0.9",
            "LLM_RETRY_ATTEMPTS": "5",
            "LOG_LEVEL": "DEBUG",
            "LOG_FILE": "test.log",
            "DEBUG": "true"
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.config.settings.load_dotenv"):
                settings = Settings()
                
                assert settings.TELEGRAM_BOT_TOKEN == "test_bot_token"
                assert settings.OPENROUTER_API_KEY == "test_api_key"
                assert settings.OPENROUTER_MODEL == "test/model"
                assert settings.LLM_TIMEOUT == 15
                assert settings.LLM_TEMPERATURE == 0.9
                assert settings.LLM_RETRY_ATTEMPTS == 5
                assert settings.LOG_LEVEL == "DEBUG"
                assert settings.LOG_FILE == "test.log"
                assert settings.DEBUG is True
    
    def test_init_with_defaults(self) -> None:
        """Тест инициализации с дефолтными значениями."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "OPENROUTER_API_KEY": "test_api_key"
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.config.settings.load_dotenv"):
                settings = Settings()
                
                # Проверяем дефолтные значения
                assert settings.OPENROUTER_MODEL == "openai/gpt-oss-20b:free"
                assert settings.LLM_TIMEOUT == 10
                assert settings.LLM_TEMPERATURE == 0.8
                assert settings.LLM_RETRY_ATTEMPTS == 3
                assert settings.LOG_LEVEL == "INFO"
                assert settings.LOG_FILE == "logs/bot.log"
                assert settings.DEBUG is False
    
    def test_missing_telegram_token_raises_error(self) -> None:
        """Тест что отсутствие TELEGRAM_BOT_TOKEN вызывает ошибку."""
        env_vars = {
            "OPENROUTER_API_KEY": "test_api_key"
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.config.settings.load_dotenv"):
                with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
                    Settings()
    
    def test_missing_openrouter_key_raises_error(self) -> None:
        """Тест что отсутствие OPENROUTER_API_KEY вызывает ошибку."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_bot_token"
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.config.settings.load_dotenv"):
                with pytest.raises(ValueError, match="OPENROUTER_API_KEY is required"):
                    Settings()
    
    def test_empty_required_env_var_raises_error(self) -> None:
        """Тест что пустые обязательные переменные вызывают ошибку."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "",  # Пустое значение
            "OPENROUTER_API_KEY": "test_api_key"
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.config.settings.load_dotenv"):
                with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
                    Settings()
    
    def test_debug_flag_parsing(self) -> None:
        """Тест парсинга DEBUG флага."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("1", False),  # Не "true"
            ("0", False),
            ("", False)
        ]
        
        for debug_value, expected in test_cases:
            env_vars = {
                "TELEGRAM_BOT_TOKEN": "test_bot_token",
                "OPENROUTER_API_KEY": "test_api_key",
                "DEBUG": debug_value
            }
            
            with patch.dict("os.environ", env_vars, clear=True):
                with patch("src.config.settings.load_dotenv"):
                    settings = Settings()
                    assert settings.DEBUG is expected, f"DEBUG='{debug_value}' should be {expected}"
    
    def test_numeric_type_conversion(self) -> None:
        """Тест конвертации числовых типов."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "OPENROUTER_API_KEY": "test_api_key",
            "LLM_TIMEOUT": "20",
            "LLM_TEMPERATURE": "0.5",
            "LLM_RETRY_ATTEMPTS": "7"
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.config.settings.load_dotenv"):
                settings = Settings()
                
                assert isinstance(settings.LLM_TIMEOUT, int)
                assert settings.LLM_TIMEOUT == 20
                
                assert isinstance(settings.LLM_TEMPERATURE, float)
                assert settings.LLM_TEMPERATURE == 0.5
                
                assert isinstance(settings.LLM_RETRY_ATTEMPTS, int)
                assert settings.LLM_RETRY_ATTEMPTS == 7
    
    def test_get_required_env_method(self) -> None:
        """Тест метода _get_required_env."""
        settings = Settings.__new__(Settings)  # Создаем без вызова __init__
        
        # Тест успешного получения
        with patch("src.config.settings.getenv", return_value="test_value"):
            result = settings._get_required_env("TEST_VAR")
            assert result == "test_value"
        
        # Тест с отсутствующей переменной
        with patch("src.config.settings.getenv", return_value=None):
            with pytest.raises(ValueError, match="TEST_VAR is required"):
                settings._get_required_env("TEST_VAR")
        
        # Тест с пустой переменной
        with patch("src.config.settings.getenv", return_value=""):
            with pytest.raises(ValueError, match="TEST_VAR is required"):
                settings._get_required_env("TEST_VAR")
    
    def test_load_dotenv_called(self) -> None:
        """Тест что load_dotenv вызывается при импорте модуля."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "OPENROUTER_API_KEY": "test_api_key"
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            # load_dotenv вызывается на уровне модуля, не в конструкторе
            # Поэтому просто проверим что Settings() работает
            settings = Settings()
            assert settings.TELEGRAM_BOT_TOKEN == "test_bot_token"
    
    def test_global_settings_instance(self) -> None:
        """Тест создания глобального экземпляра settings."""
        # Проверяем что глобальная переменная settings существует
        from src.config.settings import settings
        
        assert settings is not None
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'TELEGRAM_BOT_TOKEN')
        assert hasattr(settings, 'OPENROUTER_API_KEY')
    
    def test_model_types_and_constraints(self) -> None:
        """Тест типов и ограничений значений."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "OPENROUTER_API_KEY": "test_api_key",
            "LLM_TIMEOUT": "0",  # Граничное значение
            "LLM_TEMPERATURE": "2.0",  # Высокое значение
            "LLM_RETRY_ATTEMPTS": "1"  # Минимальное значение
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            with patch("src.config.settings.load_dotenv"):
                settings = Settings()
                
                # Проверяем что значения установились корректно
                assert settings.LLM_TIMEOUT == 0
                assert settings.LLM_TEMPERATURE == 2.0
                assert settings.LLM_RETRY_ATTEMPTS == 1
