"""
Providers package for DSPy-HELM integration.

This package provides aliases to the actual providers in the framework.
"""

# Import all providers from the framework to make them available at this level
from dspy_integration.framework.providers import (
    BaseProvider,
    ProviderResponse,
    RateLimitConfig,
    ProviderChain,
    create_provider_chain,
    get_default_provider,
    get_provider_by_name
)
from dspy_integration.framework.providers.gemini import GeminiProvider
from dspy_integration.framework.providers.groq import GroqProvider
from dspy_integration.framework.providers.huggingface import HuggingFaceProvider
from dspy_integration.framework.providers.opencode_zen import OpenCodeZenProvider
from dspy_integration.framework.providers.openrouter import OpenRouterProvider
from dspy_integration.framework.providers.puter import PuterFreeProvider
from dspy_integration.framework.providers.qwen import QwenCodeProvider

__all__ = [
    "BaseProvider",
    "ProviderResponse",
    "RateLimitConfig",
    "ProviderChain",
    "create_provider_chain",
    "get_default_provider",
    "get_provider_by_name",
    "GeminiProvider",
    "GroqProvider",
    "HuggingFaceProvider",
    "OpenCodeZenProvider",
    "OpenRouterProvider",
    "PuterFreeProvider",
    "QwenCodeProvider"
]