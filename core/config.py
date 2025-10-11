"""Configuration management for transcription system"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries. Override values take precedence.

    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary (takes precedence)

    Returns:
        Merged dictionary with override values taking precedence

    Examples:
        >>> base = {"a": 1, "b": {"c": 2, "d": 3}}
        >>> override = {"b": {"c": 99}, "e": 5}
        >>> deep_merge(base, override)
        {'a': 1, 'b': {'c': 99, 'd': 3}, 'e': 5}
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Both are dicts - recursively merge
            result[key] = deep_merge(result[key], value)
        else:
            # Override takes precedence
            result[key] = value

    return result


def load_config():
    """Load configuration from config.json - returns nested structure"""
    # Always load config.json from the project directory (where transcribe_jp.py is)
    # This ensures config.json stays with the script files

    script_dir = Path(__file__).parent.parent  # From core/config.py to project root

    # Check if we're in the project directory (has transcribe_jp.py)
    if (script_dir / "transcribe_jp.py").exists():
        # Editable install or running from source - use project directory
        config_path = script_dir / "config.json"
    else:
        # Regular install in site-packages - use current working directory
        config_path = Path.cwd() / "config.json"

    if not config_path.exists():
        print(f"ERROR: config.json not found!")
        print(f"Expected location: {config_path}")
        if (script_dir / "transcribe_jp.py").exists():
            print("\nRunning from project directory - config.json should be here:")
            print(f"  {script_dir / 'config.json'}")
        else:
            print("\nInstalled package - config.json should be in working directory:")
            print(f"  {Path.cwd() / 'config.json'}")
        sys.exit(1)

    try:
        # Load base config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"Loaded config from: {config_path}")

        # Check for config.local.json (for local overrides like API keys)
        local_config_path = config_path.parent / "config.local.json"
        if local_config_path.exists():
            try:
                with open(local_config_path, 'r', encoding='utf-8') as f:
                    local_config = json.load(f)

                # Deep merge: config.local.json overrides config.json
                config = deep_merge(config, local_config)
                print(f"Merged config from: {local_config_path}")

            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON in config.local.json: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"WARNING: Failed to load config.local.json: {e}")
                print("Continuing with base config.json only")

        # Check for ANTHROPIC_API_KEY environment variable
        env_api_key = os.environ.get('ANTHROPIC_API_KEY')
        if env_api_key:
            # Override API key with environment variable
            if 'llm' not in config:
                config['llm'] = {}
            config['llm']['anthropic_api_key'] = env_api_key
            print(f"Using ANTHROPIC_API_KEY from environment variable")

        # Store config path for reference
        config["_config_path"] = str(config_path)

        return config

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load config.json: {e}")
        sys.exit(1)
