"""
Gemini CLI Provider.

Adapter for Gemini CLI tool with support for:
- gemini-1.5-flash (FREE tier)
- gemini-1.5-pro
"""

from typing import Optional
import subprocess
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class GeminiProvider(BaseProvider):
    """Provider for Gemini CLI (free tier available)."""

    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize Gemini provider.

        Args:
            model: Model to use (default: gemini-1.5-flash free tier)
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="Gemini CLI",
            command="gemini",
            subcommand="ask",
            model=model,
            rate_limit=rate_limit,
        )

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via Gemini CLI.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse with result
        """
        start_time = time.time()

        try:
            result = subprocess.run(
                ["gemini", "ask", prompt], capture_output=True, text=True, timeout=120
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
        """Detect rate limiting indicators."""
        rate_limit_indicators = [
            "rate limit",
            "too many requests",
            "429",
            "quota exceeded",
            "user rate limit",
        ]

        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
