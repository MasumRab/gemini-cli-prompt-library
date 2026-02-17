"""
OpenRouter Provider.

Adapter for OpenRouter API with support for:
- x-ai/grok-4.1-fast:free (primary - Grok, free)
- prime-intellect/intellect-3 (free)
"""

from typing import Optional
import openai
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class OpenRouterProvider(BaseProvider):
    """Provider for OpenRouter API (OpenAI-compatible, free models)."""

    def __init__(
        self,
        model: str = "x-ai/grok-4.1-fast:free",
        api_key: Optional[str] = None,
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize OpenRouter provider.

        Args:
            model: Model to use (default: Grok free)
            api_key: OpenRouter API key
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="OpenRouter (Grok)",
            command="api",
            subcommand="openrouter",
            model=model,
            rate_limit=rate_limit,
        )
        self.api_key = (
            api_key
            or "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"
        )
        self.base_url = "https://openrouter.ai/api/v1"

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via OpenRouter API.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse with result
        """
        start_time = time.time()

        try:
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                timeout=120,
            )

            latency = time.time() - start_time

            content = response.choices[0].message.content

            return ProviderResponse(
                success=True,
                content=content,
                provider=self.name,
                model=self.model,
                latency_seconds=latency,
                tokens_used=response.usage.total_tokens if response.usage else 0,
            )

        except openai.RateLimitError as e:
            return ProviderResponse(
                success=False,
                error=str(e),
                provider=self.name,
                model=self.model,
                rate_limited=True,
                latency_seconds=time.time() - start_time,
            )

        except Exception as e:
            return ProviderResponse(
                success=False,
                error=str(e),
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time,
            )

    def _is_rate_limited(self, output: str) -> bool:
        """Detect rate limiting indicators."""
        rate_limit_indicators = [
            "rate limit",
            "too many requests",
            "429",
            "quota exceeded",
        ]

        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
