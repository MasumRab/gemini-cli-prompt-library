import os
import yaml
from typing import Dict, Any

CONFIG_PATH = os.path.expanduser("~/.dspy_tuning/config.yaml")

DEFAULT_CONFIG = {
    "dspy": {
        "enabled": True,
        "provider": None,  # None means use the default free-tier chain
        "fallback_to_keyword": True
    }
}

def load_config() -> Dict[str, Any]:
    """
    Load configuration from ~/.dspy_tuning/config.yaml.
    Returns default config if file does not exist or is invalid.
    """
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_PATH, "r") as f:
            user_config = yaml.safe_load(f)

        # Merge with defaults (shallow merge for 'dspy' key)
        config = DEFAULT_CONFIG.copy()
        if user_config and "dspy" in user_config:
            config["dspy"].update(user_config["dspy"])

        return config
    except Exception as e:
        print(f"Warning: Failed to load config from {CONFIG_PATH}: {e}")
        return DEFAULT_CONFIG

def get_dspy_config() -> Dict[str, Any]:
    """Get the 'dspy' section of the configuration."""
    return load_config().get("dspy", DEFAULT_CONFIG["dspy"])
