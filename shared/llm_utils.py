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
        """
        Generate text using Anthropic Claude

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate (0 = use 4096 as reasonable default)
            temperature: Sampling temperature

        Returns:
            Generated text response

        Note: Anthropic requires max_tokens, so 0 is converted to 4096 (reasonable default)
        """
        # Anthropic requires max_tokens parameter, use reasonable default if 0
        if max_tokens == 0:
            max_tokens = 4096  # Reasonable default for unlimited intent

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
        # Timeout priority: provider-specific > common llm.timeout > default 30
        self.timeout = ollama_config.get("timeout") or config.get("timeout", 30)
        # Context length (0 = use model's default, typically 2048-32768)
        self.context_length = ollama_config.get("context_length", 0)

        # Print configuration for visibility
        config_str = f"model={self.model}, timeout={self.timeout}s"
        if self.context_length > 0:
            config_str += f", context_length={self.context_length}"
        print(f"  - Ollama config: {config_str}")

        # Auto-manage Ollama or use external URL
        self.base_url = ollama_config.get("base_url")
        executable_path = ollama_config.get("executable_path")  # NEW: Custom executable path
        self.manager = None
        self._model_checked = False  # Track if we've already checked/pulled the model

        if not self.base_url:
            # Auto-managed mode: Initialize Ollama manager
            from shared.ollama_manager import get_ollama_manager

            self.manager = get_ollama_manager(
                model=self.model,
                executable_path=executable_path  # Pass custom path if provided
            )

            # Initialize Ollama (install if needed, start server, pull model)
            if not self.manager.initialize():
                raise RuntimeError("Failed to initialize Ollama. Please install manually from https://ollama.com/download")

            self.base_url = self.manager.base_url
            self._model_checked = True  # Model was checked during initialize()
        else:
            # External mode: Use provided base_url (backward compatible)
            # Can also use custom executable_path with external server
            from shared.ollama_manager import get_ollama_manager

            self.manager = get_ollama_manager(
                model=self.model,
                executable_path=executable_path,
                base_url=self.base_url  # Use external server
            )

            # Just verify external server is reachable
            if not self.manager.start():
                raise RuntimeError(f"Cannot reach external Ollama server at {self.base_url}")

            self._model_checked = False  # Need to check model on external server
            print(f"  - Using external Ollama server at {self.base_url}")

    def _ensure_model(self) -> bool:
        """
        Ensure model is available before generating.
        If using external server, checks if model exists and attempts to pull if not.

        Returns:
            True if model is available, False otherwise
        """
        # Skip if already checked
        if self._model_checked:
            return True

        # For external servers, try to check and pull model if needed
        if not self.manager:
            try:
                # Check if model exists via API tags endpoint
                response = self.requests.get(f"{self.base_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]

                    if self.model in model_names:
                        print(f"  - Model {self.model} found on external server")
                        self._model_checked = True
                        return True

                    # Model not found - try to pull it
                    print(f"  - Model {self.model} not found on external server, attempting to pull...")
                    print(f"  - This may take several minutes depending on model size")

                    pull_response = self.requests.post(
                        f"{self.base_url}/api/pull",
                        json={"name": self.model},
                        stream=True,
                        timeout=1800  # 30 minute timeout
                    )

                    if pull_response.status_code != 200:
                        print(f"  - ERROR: Failed to pull model (HTTP {pull_response.status_code})")
                        return False

                    # Show simple progress
                    import json
                    for line in pull_response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                status = data.get("status", "")
                                if status and status != "pulling manifest":
                                    completed = data.get("completed", 0)
                                    total = data.get("total", 0)
                                    if total > 0:
                                        percent = (completed / total) * 100
                                        print(f"\r  - Downloading: {percent:.1f}%", end="", flush=True)
                            except:
                                pass

                    print(f"\n  - Model {self.model} pulled successfully")
                    self._model_checked = True
                    return True

            except Exception as e:
                print(f"  - Warning: Could not verify model availability: {e}")
                # Continue anyway - let generate() fail with proper error if needed

        self._model_checked = True
        return True

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """
        Generate text using Ollama

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate (0 = unlimited)
            temperature: Sampling temperature

        Returns:
            Generated text response
        """
        # Ensure model is available (checks and pulls if needed)
        if not self._ensure_model():
            raise RuntimeError(f"Model {self.model} is not available. Please pull it manually: ollama pull {self.model}")

        url = f"{self.base_url}/api/generate"

        # Build options
        options = {"temperature": temperature}

        # num_predict: max tokens to generate (0 = unlimited)
        if max_tokens > 0:
            options["num_predict"] = max_tokens

        # num_ctx: context window size (0 = use model default)
        # Reducing context_length decreases VRAM usage, allowing larger models to fit in GPU
        if self.context_length > 0:
            options["num_ctx"] = self.context_length

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }

        try:
            response = self.requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except self.requests.exceptions.HTTPError as e:
            # Check if it's a model not found error
            if e.response.status_code == 404:
                raise RuntimeError(f"Model '{self.model}' not found on Ollama server. Please pull it: ollama pull {self.model}")
            raise RuntimeError(f"Ollama API request failed (HTTP {e.response.status_code}): {e}")
        except self.requests.exceptions.Timeout:
            raise RuntimeError(
                f"Ollama request timed out after {self.timeout}s.\n"
                f"  Possible causes:\n"
                f"  - Model '{self.model}' is too slow (try smaller model or increase timeout)\n"
                f"  - Server is under heavy load\n"
                f"  - Using CPU instead of GPU (check Ollama logs)\n"
                f"  Solution: Increase timeout in config: llm.timeout = 60 or more"
            )
        except self.requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                f"Cannot connect to Ollama server at {self.base_url}.\n"
                f"  Possible causes:\n"
                f"  - Ollama server not running (start with: ollama serve)\n"
                f"  - Wrong base_url in config (check llm.ollama.base_url)\n"
                f"  - Server crashed (check Ollama logs)\n"
                f"  Solution: Verify Ollama is running and accessible"
            )
        except self.requests.exceptions.ChunkedEncodingError:
            raise RuntimeError(
                f"Ollama server connection interrupted mid-response.\n"
                f"  Possible causes:\n"
                f"  - Server crashed during generation\n"
                f"  - Network issues\n"
                f"  - Out of memory (model too large for available VRAM/RAM)\n"
                f"  Solution: Check Ollama server logs for errors"
            )
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Invalid JSON response from Ollama server.\n"
                f"  Server may have returned an error message instead of JSON.\n"
                f"  Solution: Check Ollama server logs for details"
            )
        except Exception as e:
            raise RuntimeError(f"Ollama API request failed: {type(e).__name__}: {e}")

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
        """
        Generate text using OpenAI

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate (0 = None/unlimited, up to model's limit)
            temperature: Sampling temperature

        Returns:
            Generated text response

        Note: OpenAI allows None for max_tokens, which means no limit (up to model's context)
        """
        # OpenAI allows None for max_tokens (no limit, up to model context)
        if max_tokens == 0:
            max_tokens = None

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
        stage_name: Optional stage name to use stage-specific LLM config (e.g., "text_polishing", "segment_splitting")

    Returns:
        LLMProvider instance or None if provider cannot be created

    Stage-specific overrides supported:
    - llm_provider: Override provider (e.g., use Ollama for splitting, Claude for polishing)
    - llm_timeout: Override timeout for this stage (useful for large models or complex tasks)
    """
    llm_config = config.get("llm", {}).copy()  # Copy to avoid modifying original

    # Check for stage-specific overrides
    if stage_name:
        stage_config = config.get(stage_name, {})

        # Override provider if specified
        if "llm_provider" in stage_config:
            provider_name = stage_config.get("llm_provider")
            llm_config["provider"] = provider_name

        # Override timeout if specified (allows longer timeout for specific stages)
        if "llm_timeout" in stage_config:
            timeout = stage_config.get("llm_timeout")
            # Apply timeout to both common config and provider-specific config
            llm_config["timeout"] = timeout  # Common timeout
            # Apply timeout to provider-specific config for backwards compatibility
            provider_name = llm_config.get("provider", "anthropic").lower()
            if provider_name == "ollama":
                if "ollama" not in llm_config:
                    llm_config["ollama"] = {}
                llm_config["ollama"]["timeout"] = timeout
            elif provider_name == "openai":
                if "openai" not in llm_config:
                    llm_config["openai"] = {}
                llm_config["openai"]["timeout"] = timeout
            # Note: Anthropic SDK handles timeouts internally

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
