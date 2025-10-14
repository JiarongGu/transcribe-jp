#!/usr/bin/env python3
"""
Integration tests for Ollama provider

These tests verify Ollama integration with real server (mocked or real).
They test: installation detection, server management, model pulling, generation, timeout handling.

Run with: python -X utf8 -m pytest tests/integration/test_ollama.py -v
"""

import pytest
import sys
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.llm_utils import OllamaProvider, create_llm_provider
from shared.ollama_manager import OllamaManager


class TestOllamaInstallation:
    """Test Ollama installation detection"""

    def test_installation_check(self):
        """Test if Ollama installation can be detected"""
        manager = OllamaManager(model="llama3.2:3b")

        # Should detect whether Ollama is installed
        is_installed = manager.is_installed()

        # Result should be boolean
        assert isinstance(is_installed, bool)

        # If installed, executable should be found
        if is_installed:
            exe = manager._get_ollama_executable()
            assert exe is not None
            assert exe.exists()

    def test_executable_detection_windows(self):
        """Test Ollama executable detection on Windows"""
        import platform
        if platform.system() != "Windows":
            pytest.skip("Windows-only test")

        manager = OllamaManager()

        # Should check common Windows locations
        exe = manager._get_ollama_executable()

        # Either found or not found (no errors)
        assert exe is None or (exe.exists() and exe.name == "ollama.exe")

    @patch('shutil.which')
    def test_installation_not_found(self, mock_which):
        """Test behavior when Ollama is not installed"""
        mock_which.return_value = None

        manager = OllamaManager()
        assert not manager.is_installed()


class TestOllamaServerManagement:
    """Test Ollama server lifecycle management"""

    @pytest.fixture
    def manager(self):
        """Create OllamaManager instance"""
        return OllamaManager(model="llama3.2:3b")

    def test_server_running_check(self, manager):
        """Test server running detection"""
        # Should not raise exception
        is_running = manager.is_running()
        assert isinstance(is_running, bool)

    @patch('requests.get')
    def test_server_running_true(self, mock_get, manager):
        """Test server detected as running"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert manager.is_running() is True

    @patch('requests.get')
    def test_server_running_false_connection_error(self, mock_get, manager):
        """Test server detected as not running (connection error)"""
        mock_get.side_effect = Exception("Connection refused")

        assert manager.is_running() is False

    @patch('requests.get')
    def test_server_running_false_wrong_status(self, mock_get, manager):
        """Test server detected as not running (wrong status code)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        assert manager.is_running() is False


class TestOllamaModelManagement:
    """Test Ollama model availability and pulling"""

    @pytest.fixture
    def manager(self):
        """Create OllamaManager instance"""
        return OllamaManager(model="llama3.2:3b")

    @patch('requests.get')
    def test_model_available_check(self, mock_get, manager):
        """Test model availability detection"""
        # Mock server response with model list
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:3b"},
                {"name": "qwen3:4b"}
            ]
        }
        mock_get.return_value = mock_response

        # Mock server as running
        with patch.object(manager, 'is_running', return_value=True):
            assert manager.is_model_available() is True

    @patch('requests.get')
    def test_model_not_available(self, mock_get, manager):
        """Test model not found"""
        # Mock server response without model
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "other-model:1b"}
            ]
        }
        mock_get.return_value = mock_response

        with patch.object(manager, 'is_running', return_value=True):
            assert manager.is_model_available() is False

    @patch('requests.get')
    @patch('requests.post')
    def test_model_pulling_progress(self, mock_post, mock_get, manager):
        """Test model pulling with progress tracking"""
        # Mock server running
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response

        # Mock pull response with progress
        mock_pull_response = Mock()
        mock_pull_response.status_code = 200

        # Simulate progress stream
        progress_data = [
            b'{"status":"pulling manifest"}',
            b'{"status":"downloading","completed":1000,"total":2000}',
            b'{"status":"downloading","completed":2000,"total":2000}',
            b'{"status":"verifying sha256 digest"}',
            b'{"status":"success"}'
        ]
        mock_pull_response.iter_lines.return_value = progress_data
        mock_post.return_value = mock_pull_response

        with patch.object(manager, 'is_running', return_value=True):
            result = manager.ensure_model_available()

            # Should succeed
            assert result is True

            # Should have called POST to /api/pull
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "/api/pull" in call_args[0][0]

    @patch('requests.post')
    def test_model_pulling_timeout(self, mock_post, manager):
        """Test model pulling timeout handling"""
        import requests

        # Mock pull timeout
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

        with patch.object(manager, 'is_running', return_value=True):
            with patch.object(manager, 'is_model_available', return_value=False):
                result = manager.ensure_model_available()

                # Should fail gracefully
                assert result is False


class TestOllamaProviderGeneration:
    """Test Ollama text generation"""

    @pytest.fixture
    def config(self):
        """Basic Ollama config"""
        return {
            "provider": "ollama",
            "timeout": 30,
            "max_tokens": 512,
            "temperature": 0.0,
            "ollama": {
                "model": "llama3.2:3b"
            }
        }

    @patch('requests.post')
    def test_generation_success(self, mock_post, config):
        """Test successful text generation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Generated text response"
        }
        mock_post.return_value = mock_response

        # Create provider (skip initialization)
        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, '__init__', lambda x, y: None):
                provider = OllamaProvider.__new__(OllamaProvider)
                provider.model = "llama3.2:3b"
                provider.timeout = 30
                provider.base_url = "http://localhost:11434"
                provider.requests = __import__('requests')
                provider.manager = None
                provider._model_checked = True

                result = provider.generate("Test prompt", max_tokens=512, temperature=0.0)

                assert result == "Generated text response"

                # Verify request payload
                call_args = mock_post.call_args
                payload = call_args[1]['json']
                assert payload['model'] == "llama3.2:3b"
                assert payload['prompt'] == "Test prompt"
                assert payload['options']['temperature'] == 0.0
                assert payload['options']['num_predict'] == 512

    @patch('requests.post')
    def test_generation_timeout(self, mock_post, config):
        """Test generation timeout error"""
        import requests

        # Mock timeout
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, '__init__', lambda x, y: None):
                provider = OllamaProvider.__new__(OllamaProvider)
                provider.model = "qwen3:4b"
                provider.timeout = 30
                provider.base_url = "http://localhost:11434"
                provider.requests = __import__('requests')
                provider.manager = None
                provider._model_checked = True

                with pytest.raises(RuntimeError) as exc_info:
                    provider.generate("Test prompt")

                # Should mention timeout and provide solutions
                error_msg = str(exc_info.value)
                assert "timed out" in error_msg.lower()
                assert "30s" in error_msg
                assert "increase timeout" in error_msg.lower()

    @patch('requests.post')
    def test_generation_connection_error(self, mock_post, config):
        """Test generation connection error"""
        import requests

        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, '__init__', lambda x, y: None):
                provider = OllamaProvider.__new__(OllamaProvider)
                provider.model = "llama3.2:3b"
                provider.timeout = 30
                provider.base_url = "http://localhost:11434"
                provider.requests = __import__('requests')
                provider.manager = None
                provider._model_checked = True

                with pytest.raises(RuntimeError) as exc_info:
                    provider.generate("Test prompt")

                # Should mention connection and provide solutions
                error_msg = str(exc_info.value)
                assert "connect" in error_msg.lower()
                assert "http://localhost:11434" in error_msg

    @patch('requests.post')
    def test_generation_model_not_found(self, mock_post, config):
        """Test generation with model not found"""
        # Mock 404 error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        mock_post.return_value.raise_for_status.side_effect = __import__('requests').exceptions.HTTPError(response=mock_response)

        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, '__init__', lambda x, y: None):
                provider = OllamaProvider.__new__(OllamaProvider)
                provider.model = "nonexistent:1b"
                provider.timeout = 30
                provider.base_url = "http://localhost:11434"
                provider.requests = __import__('requests')
                provider.manager = None
                provider._model_checked = True

                with pytest.raises(RuntimeError) as exc_info:
                    provider.generate("Test prompt")

                # Should mention model not found
                error_msg = str(exc_info.value)
                assert "not found" in error_msg.lower()
                assert "nonexistent:1b" in error_msg


class TestOllamaProviderConfiguration:
    """Test Ollama provider configuration options"""

    def test_timeout_priority_provider_specific(self):
        """Test provider-specific timeout takes priority"""
        config = {
            "timeout": 60,  # Common timeout
            "ollama": {
                "model": "llama3.2:3b",
                "timeout": 45  # Provider-specific (should win)
            }
        }

        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, 'initialize', return_value=True):
                provider = OllamaProvider(config)

                # Should use provider-specific timeout
                assert provider.timeout == 45

    def test_timeout_fallback_to_common(self):
        """Test fallback to common timeout"""
        config = {
            "timeout": 60,  # Common timeout
            "ollama": {
                "model": "llama3.2:3b"
                # No provider-specific timeout
            }
        }

        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, 'initialize', return_value=True):
                provider = OllamaProvider(config)

                # Should use common timeout
                assert provider.timeout == 60

    def test_max_tokens_unlimited(self):
        """Test max_tokens=0 for unlimited generation"""
        config = {
            "ollama": {
                "model": "llama3.2:3b"
            }
        }

        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "text"}
            mock_post.return_value = mock_response

            with patch('shared.llm_utils.get_ollama_manager'):
                with patch.object(OllamaProvider, '__init__', lambda x, y: None):
                    provider = OllamaProvider.__new__(OllamaProvider)
                    provider.model = "llama3.2:3b"
                    provider.timeout = 30
                    provider.base_url = "http://localhost:11434"
                    provider.requests = __import__('requests')
                    provider.manager = None
                    provider._model_checked = True

                    provider.generate("Test", max_tokens=0)

                    # Should NOT include num_predict in options
                    call_args = mock_post.call_args
                    payload = call_args[1]['json']
                    assert 'num_predict' not in payload['options']


class TestOllamaStageSpecificConfig:
    """Test stage-specific LLM configuration"""

    def test_stage_timeout_override(self):
        """Test stage-specific timeout override"""
        config = {
            "llm": {
                "provider": "ollama",
                "timeout": 45,
                "ollama": {
                    "model": "qwen3:8b"
                }
            },
            "text_polishing": {
                "enable": True,
                "llm_timeout": 120  # Stage-specific override
            }
        }

        # Create provider for text_polishing stage
        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, 'initialize', return_value=True):
                provider = create_llm_provider(config, stage_name="text_polishing")

                # Should use stage-specific timeout
                assert provider.timeout == 120

    def test_stage_provider_override(self):
        """Test stage-specific provider override"""
        config = {
            "llm": {
                "provider": "ollama",  # Default
                "ollama": {
                    "model": "llama3.2:3b"
                },
                "anthropic": {
                    "api_key": "test-key",
                    "model": "claude-3-5-haiku-20241022"
                }
            },
            "text_polishing": {
                "enable": True,
                "llm_provider": "anthropic"  # Override to Anthropic
            }
        }

        # Create provider for text_polishing stage
        with patch('anthropic.Anthropic'):
            provider = create_llm_provider(config, stage_name="text_polishing")

            # Should be Anthropic provider
            from shared.llm_utils import AnthropicProvider
            assert isinstance(provider, AnthropicProvider)


class TestOllamaErrorMessages:
    """Test Ollama error message quality"""

    @patch('requests.post')
    def test_timeout_error_message_quality(self, mock_post):
        """Test timeout error provides helpful diagnostics"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, '__init__', lambda x, y: None):
                provider = OllamaProvider.__new__(OllamaProvider)
                provider.model = "qwen3:32b"
                provider.timeout = 45
                provider.base_url = "http://localhost:11434"
                provider.requests = __import__('requests')
                provider.manager = None
                provider._model_checked = True

                with pytest.raises(RuntimeError) as exc_info:
                    provider.generate("Test")

                error_msg = str(exc_info.value)

                # Should contain helpful information
                assert "45s" in error_msg  # Shows actual timeout
                assert "qwen3:32b" in error_msg  # Shows model
                assert "Possible causes" in error_msg
                assert "Solution" in error_msg
                assert "increase timeout" in error_msg.lower()

    @patch('requests.post')
    def test_connection_error_message_quality(self, mock_post):
        """Test connection error provides helpful diagnostics"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        with patch('shared.llm_utils.get_ollama_manager'):
            with patch.object(OllamaProvider, '__init__', lambda x, y: None):
                provider = OllamaProvider.__new__(OllamaProvider)
                provider.model = "llama3.2:3b"
                provider.timeout = 30
                provider.base_url = "http://localhost:11434"
                provider.requests = __import__('requests')
                provider.manager = None
                provider._model_checked = True

                with pytest.raises(RuntimeError) as exc_info:
                    provider.generate("Test")

                error_msg = str(exc_info.value)

                # Should contain helpful information
                assert "http://localhost:11434" in error_msg  # Shows URL
                assert "Possible causes" in error_msg
                assert "Solution" in error_msg
                assert "ollama serve" in error_msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
