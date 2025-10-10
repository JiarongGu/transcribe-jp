"""Configuration management for transcription system"""

import json
import sys
from pathlib import Path


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
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Store config path for reference
        config["_config_path"] = str(config_path)

        print(f"Loaded config from: {config_path}")
        return config

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load config.json: {e}")
        sys.exit(1)
