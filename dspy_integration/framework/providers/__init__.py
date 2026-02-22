"""
Provider module for DSPy-HELM.

Provides unified interface for:
- Groq (FREE tier - fast inference!)
- HuggingFace Inference API (FREE tier - no API key needed!)
- Puter.js (truly FREE but browser-only)
- OpenCode Zen (requires API key - paid)
- OpenRouter (requires API key)
- Google Gemini (requires API key)

Priority: Groq → HuggingFace → OpenRouter → Gemini (all with free tiers!)
"""
import logging
from .base import BaseProvider, ProviderResponse, RateLimitConfig, ProviderChain
from .groq import GroqProvider
from .huggingface import HuggingFaceProvider
from .puter import PuterFreeProvider
from .opencode_zen import OpenCodeZenProvider
from .openrouter import OpenRouterProvider
from .gemini import GeminiProvider

logger = logging.getLogger(__name__)

# Import configuration
try:
    from ..config import get_dspy_config
except ImportError:
    # Fallback if config module not found or import error
    def get_dspy_config():
        return {
            "enabled": False,
            "provider": None,
            "fallback_to_keyword": False
        }


def create_provider_chain() -> ProviderChain:
    """
    Create provider chain based on configuration.

    If specific provider is configured in ~/.dspy_tuning/config.yaml, uses that.
    Otherwise defaults to: Groq → HuggingFace → OpenRouter → Gemini (all with free tiers!)

    Returns:
        ProviderChain with configured providers
    """
    config = get_dspy_config()
    forced_provider = config.get("provider")

    # If user explicitly sets a provider, use only that one
    if forced_provider and forced_provider.lower() not in ["auto", "none", "null"]:
        try:
            provider = get_provider_by_name(forced_provider.lower())
            return ProviderChain([provider])
        except ValueError as e:
            logger.warning(f"Configured provider '{forced_provider}' not found. Falling back to default chain. Error: {e}")
            # Fall through to default chain

    # Default Chain
    providers = [
        # Primary: Groq - FAST, free tier available!
        GroqProvider(
            model="llama-3.3-70b-versatile",
            rate_limit=RateLimitConfig(enabled=True, max_retries=3, backoff_factor=1.0),
        ),
        # Fallback 1: HuggingFace - FREE, no API key needed!
        HuggingFaceProvider(
            model="meta-llama/Llama-3.2-3B-Instruct",
            rate_limit=RateLimitConfig(enabled=True, max_retries=3, backoff_factor=1.0),
        ),
        # Fallback 2: OpenRouter (requires API key)
        OpenRouterProvider(
            model="x-ai/grok-4.1-fast:free",
            rate_limit=RateLimitConfig(enabled=True, max_retries=3, backoff_factor=1.0),
        ),
        # Fallback 3: Gemini (requires API key)
        GeminiProvider(
            model="gemini-1.5-flash",
            rate_limit=RateLimitConfig(enabled=True, max_retries=3, backoff_factor=2.0),
        ),
    ]

    return ProviderChain(providers)


def get_default_provider() -> BaseProvider:
    """
    Get the default (primary) provider based on config.
    If no config, returns Groq (fast, free tier available).
    """
    config = get_dspy_config()
    forced_provider = config.get("provider")

    if forced_provider and forced_provider.lower() not in ["auto", "none", "null"]:
        try:
            return get_provider_by_name(forced_provider.lower())
        except ValueError as e:
            logger.warning(f"Configured provider '{forced_provider}' not found. Falling back to Groq. Error: {e}")
            pass

    return GroqProvider(
        model="llama-3.3-70b-versatile",
        rate_limit=RateLimitConfig(enabled=True, max_retries=3, backoff_factor=1.0),
    )


def get_provider_by_name(name: str) -> BaseProvider:
    """
    Get a specific provider by name.

    Args:
        name: Provider name (groq, huggingface, puter, opencode_zen, openrouter, google, gemini)

    Returns:
        Provider instance

    Raises:
        ValueError: If provider not found
    """
    providers = {
        "groq": GroqProvider,
        "huggingface": HuggingFaceProvider,
        "puter": PuterFreeProvider,
        "opencode_zen": OpenCodeZenProvider,
        "openrouter": OpenRouterProvider,
        "google": GeminiProvider,
        "gemini": GeminiProvider,  # Alias for google/gemini
    }

    if name not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(f"Unknown provider: '{name}'. Available: {available}")

    return providers[name]()


__all__ = [
    "BaseProvider",
    "ProviderResponse",
    "RateLimitConfig",
    "ProviderChain",
    "GroqProvider",
    "HuggingFaceProvider",
    "PuterFreeProvider",
    "OpenCodeZenProvider",
    "OpenRouterProvider",
    "GeminiProvider",
    "create_provider_chain",
    "get_default_provider",
    "get_provider_by_name",
]
