"""
OpenCode Zen Provider.

Adapter for OpenCode Zen gateway with support for:
- grok-code (Grok Code Fast 1 - FREE)
- minimax-m2.1-free (MiniMax M2.1 - FREE)
- glm-4.7-free (GLM 4.7 - FREE)
- big-pickle (FREE)
- gpt-5-nano (FREE)
"""

from typing import Optional
import openai
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class OpenCodeZenProvider(BaseProvider):
    """Provider for OpenCode Zen gateway (OpenAI-compatible, all models FREE)."""

    def __init__(
        self,
        model: str = "grok-code",
        api_key: Optional[str] = None,
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize OpenCode Zen provider.

        Args:
            model: Model to use (default: grok-code)
            api_key: Not required for free models (use placeholder)
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="OpenCode Zen (Grok Code Fast)",
            command="api",
            subcommand="opencode-zen",
            model=model,
            rate_limit=rate_limit,
        )
        self.api_key = api_key or "not-required"  # Free models don't need key
        self.base_url = "https://opencode.ai/zen/v1/chat/completions"

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via OpenCode Zen API.

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
