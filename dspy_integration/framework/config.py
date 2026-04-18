import os
import yaml
import copy
import logging
from typing import Dict, Any

CONFIG_PATH = os.path.expanduser("~/.dspy_tuning/config.yaml")

DEFAULT_CONFIG = {
    "dspy": {
        "enabled": True,
        "provider": None,  # None means use the default free-tier chain
        "fallback_to_keyword": True,
    }
}

logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """
    Load configuration from ~/.dspy_tuning/config.yaml.
    Returns default config if file does not exist or is invalid.
    """
    if not os.path.exists(CONFIG_PATH):
        return copy.deepcopy(DEFAULT_CONFIG)

    try:
        with open(CONFIG_PATH, "r") as f:
            user_config = yaml.safe_load(f)

        # Deep copy defaults to avoid mutation
        config = copy.deepcopy(DEFAULT_CONFIG)

        if isinstance(user_config, dict) and isinstance(user_config.get("dspy"), dict):
            config["dspy"].update(user_config["dspy"])
        elif user_config is not None and not isinstance(user_config, dict):
            logger.warning(
                f"Invalid config shape in {CONFIG_PATH}: expected mapping at root."
            )

        return config
    except (yaml.YAMLError, OSError) as e:
        logger.warning(f"Failed to load config from {CONFIG_PATH}: {e}")
        return copy.deepcopy(DEFAULT_CONFIG)


def get_dspy_config() -> Dict[str, Any]:
    """Get the 'dspy' section of the configuration."""
    return load_config().get("dspy", DEFAULT_CONFIG["dspy"])
