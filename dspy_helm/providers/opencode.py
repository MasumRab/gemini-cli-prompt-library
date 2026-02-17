"""
OpenCode CLI Provider.

Adapter for OpenCode CLI tool with support for:
- gpt-4o-mini (OpenAI FREE tier)
"""

from typing import Optional
import subprocess
import json
import logging
from .base import BaseProvider, ProviderResponse, RateLimitConfig

logger = logging.getLogger(__name__)


class OpenCodeProvider(BaseProvider):
    """Provider for OpenCode CLI using OpenAI free tier."""

    def __init__(
        self, model: str = "gpt-4o-mini", rate_limit: Optional[RateLimitConfig] = None
    ):
        """
        Initialize OpenCode provider (OpenAI FREE tier).

        Args:
            model: Model to use (gpt-4o-mini)
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="OpenCode CLI (OpenAI Free)",
            command="opencode",
            subcommand="ask",
            model=model,
            rate_limit=rate_limit,
        )

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via OpenCode CLI.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments (ignored)

        Returns:
            ProviderResponse with result
        """
        import time

        start_time = time.time()

        try:
            result = subprocess.run(
                ["opencode", "ask", prompt], capture_output=True, text=True, timeout=120
            )

            latency = time.time() - start_time

            if result.returncode != 0:
                error_output = result.stderr or result.stdout

                rate_limited = self._is_rate_limited(error_output)

                return ProviderResponse(
                    success=False,
                    error=error_output,
                    provider=self.name,
                    model=self.model,
                    rate_limited=rate_limited,
                    latency_seconds=latency,
                )

            return ProviderResponse(
                success=True,
                content=result.stdout.strip(),
                provider=self.name,
                model=self.model,
                latency_seconds=latency,
            )

        except subprocess.TimeoutExpired:
            return ProviderResponse(
                success=False,
                error="Command timed out after 120 seconds",
                provider=self.name,
                model=self.model,
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
        """
        Detect if output indicates rate limiting.

        Args:
            output: CLI output or error message

        Returns:
            True if rate limited
        """
        rate_limit_indicators = [
            "rate limit",
            "rate_limit",
            "too many requests",
            "429",
            "exceeded quota",
            "capacity",
            "try again later",
            "free tier",
        ]

        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
