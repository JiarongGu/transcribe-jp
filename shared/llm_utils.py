"""Unified LLM provider abstraction for flexible model usage"""

import os
import json
from typing import Optional, Dict, Any, List


class LLMProvider:
    """Base class for LLM providers"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Generate text from prompt. Returns raw text response."""
        raise NotImplementedError("Subclasses must implement generate()")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from anthropic import Anthropic
            self.anthropic = Anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")

        # Get provider-specific config
        anthropic_config = config.get("anthropic", {})

        # Get API key (check both old and new locations for backward compatibility)
        self.api_key = anthropic_config.get("api_key") or config.get("anthropic_api_key")
        if not self.api_key:
            api_key_env = anthropic_config.get("api_key_env") or config.get("api_key_env", "ANTHROPIC_API_KEY")
            self.api_key = os.environ.get(api_key_env)

        if not self.api_key:
            raise ValueError("Anthropic API key not found in config or environment")

        self.client = self.anthropic(api_key=self.api_key)
        self.model = anthropic_config.get("model") or config.get("model", "claude-3-5-haiku-20241022")

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Generate text using Anthropic Claude"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()


class OllamaProvider(LLMProvider):
    """Ollama local model provider with automatic management"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests package not installed. Install with: pip install requests")

        # Get provider-specific config
        ollama_config = config.get("ollama", {})

        # Model configuration
        self.model = ollama_config.get("model") or config.get("model", "llama3.2:3b")
        self.timeout = ollama_config.get("timeout") or config.get("timeout", 30)

        # Auto-manage Ollama or use external URL
        self.base_url = ollama_config.get("base_url")
        self.manager = None

        if not self.base_url:
            # Auto-managed mode: Initialize Ollama manager
            from shared.ollama_manager import get_ollama_manager

            self.manager = get_ollama_manager(model=self.model)

            # Initialize Ollama (install if needed, start server, pull model)
            if not self.manager.initialize():
                raise RuntimeError("Failed to initialize Ollama. Please install manually from https://ollama.com/download")

            self.base_url = self.manager.base_url
        else:
            # External mode: Use provided base_url (backward compatible)
            print(f"  - Using external Ollama server at {self.base_url}")

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Generate text using Ollama"""
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = self.requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Ollama API request failed: {e}")

    def cleanup(self):
        """Stop managed Ollama server if running"""
        if self.manager:
            self.manager.stop()

    def __del__(self):
        """Cleanup on object destruction"""
        self.cleanup()


class OpenAIProvider(LLMProvider):
    """OpenAI provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from openai import OpenAI
            self.openai = OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        # Get provider-specific config
        openai_config = config.get("openai", {})

        # Get API key (check both old and new locations for backward compatibility)
        self.api_key = openai_config.get("api_key") or config.get("openai_api_key")
        if not self.api_key:
            api_key_env = openai_config.get("api_key_env") or config.get("api_key_env", "OPENAI_API_KEY")
            self.api_key = os.environ.get(api_key_env)

        if not self.api_key:
            raise ValueError("OpenAI API key not found in config or environment")

        self.client = self.openai(api_key=self.api_key)
        self.model = openai_config.get("model") or config.get("model", "gpt-4o-mini")

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Generate text using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()


def create_llm_provider(config: Dict[str, Any], stage_name: Optional[str] = None) -> Optional[LLMProvider]:
    """
    Create an LLM provider based on configuration.

    Args:
        config: Full pipeline configuration
        stage_name: Optional stage name to use stage-specific LLM config

    Returns:
        LLMProvider instance or None if provider cannot be created
    """
    llm_config = config.get("llm", {})

    # Check for stage-specific provider override
    if stage_name:
        stage_config = config.get(stage_name, {})
        if "llm_provider" in stage_config:
            # Stage overrides provider - use global llm config with different provider
            provider_name = stage_config.get("llm_provider")
            llm_config = {**llm_config, "provider": provider_name}

    provider_name = llm_config.get("provider", "anthropic").lower()

    try:
        if provider_name == "anthropic":
            return AnthropicProvider(llm_config)
        elif provider_name == "ollama":
            return OllamaProvider(llm_config)
        elif provider_name == "openai":
            return OpenAIProvider(llm_config)
        else:
            print(f"  - Warning: Unknown LLM provider '{provider_name}', LLM features disabled")
            return None
    except (ImportError, ValueError) as e:
        print(f"  - Warning: Failed to initialize {provider_name} provider: {e}")
        return None


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Parse JSON response from LLM, handling markdown code blocks.

    Args:
        response_text: Raw LLM response text

    Returns:
        Parsed JSON as dictionary

    Raises:
        json.JSONDecodeError: If response cannot be parsed as JSON
    """
    text = response_text.strip()

    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split('\n')
        json_lines = []
        in_code_block = False
        for line in lines:
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block or (not line.startswith("```") and json_lines):
                json_lines.append(line)
        text = '\n'.join(json_lines).strip()

    return json.loads(text)
