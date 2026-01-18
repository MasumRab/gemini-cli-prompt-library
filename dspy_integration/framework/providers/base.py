"""
Base classes for CLI tool providers.

Provides abstraction layer for different CLI tools
following the Strategy pattern for provider rotation.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import time
import logging
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


@dataclass
class ProviderResponse:
    """Response from a provider."""

    success: bool
    content: str = ""
    provider: str = ""
    model: str = ""
    error: Optional[str] = None
    tokens_used: int = 0
    latency_seconds: float = 0.0
    rate_limited: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    enabled: bool = True
    max_retries: int = 3
    backoff_factor: float = 1.0
    max_backoff: float = 60.0


class BaseProvider(ABC):
    """Abstract base class for CLI providers."""

    def __init__(
        self,
        name: str,
        command: str,
        subcommand: str,
        model: str,
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize provider.

        Args:
            name: Provider display name
            command: CLI command to run
            subcommand: CLI subcommand (e.g., "ask")
            model: Default model to use
            rate_limit: Rate limiting configuration
        """
        self.name = name
        self.command = command
        self.subcommand = subcommand
        self.model = model
        self.rate_limit = rate_limit or RateLimitConfig()

        self._last_request_time = 0.0
        self._retry_count = 0

    @abstractmethod
    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute the CLI command.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse with result or error
        """
        ...

    def call(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Call the provider with retry logic for rate limits.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse with result
        """
        if not self.rate_limit.enabled:
            return self._execute_cli(prompt, **kwargs)

        max_retries = self.rate_limit.max_retries
        backoff = self.rate_limit.backoff_factor

        for attempt in range(max_retries + 1):
            response = self._execute_cli(prompt, **kwargs)

            if response.success:
                self._retry_count = 0
                return response

            if not response.rate_limited:
                return response

            if attempt < max_retries:
                wait_time = min(backoff * (2**attempt), self.rate_limit.max_backoff)
                logger.warning(
                    f"Rate limited by {self.name}, retrying in {wait_time}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries exceeded for {self.name}")
                return response

        return ProviderResponse(
            success=False,
            error="Max retries exceeded",
            provider=self.name,
            model=self.model,
        )

    def __repr__(self) -> str:
        return f"{self.name}(model={self.model})"


class ProviderChain:
    """
    Chain of providers with failover support.

    Manages rotation through providers when rate limits
    are encountered.
    """

    def __init__(self, providers: List[BaseProvider]):
        """
        Initialize provider chain.

        Args:
            providers: List of providers in priority order
        """
        self.providers = providers
        self._current_index = 0

    def call(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Call providers in sequence with failover.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse from first successful provider
        """
        last_error = None

        for provider in self.providers:
            response = provider.call(prompt, **kwargs)

            if response.success:
                return response

            last_error = response.error
            logger.info(
                f"Provider {provider.name} failed: {response.error}. "
                f"Trying next provider..."
            )

        return ProviderResponse(
            success=False,
            error=f"All providers failed: {last_error}",
            provider="none",
            model="none",
        )

    def add_provider(self, provider: BaseProvider) -> None:
        """Add provider to chain."""
        self.providers.append(provider)

    def set_fallback_order(self, provider_names: List[str]) -> None:
        """
        Reorder providers by name.

        Args:
            provider_names: List of provider names in desired order
        """
        name_to_provider = {p.name: p for p in self.providers}
        self.providers = [
            name_to_provider[name]
            for name in provider_names
            if name in name_to_provider
        ]
