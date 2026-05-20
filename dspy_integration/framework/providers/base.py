"""
Base classes for CLI tool providers.

Provides abstraction layer for different CLI tools
following the Strategy pattern for provider rotation.
"""

from dspy_helm.providers.base import (
    ProviderResponse,
    RateLimitConfig,
    BaseProvider,
    ProviderChain,
)

__all__ = [
    "ProviderResponse",
    "RateLimitConfig",
    "BaseProvider",
    "ProviderChain",
]
