"""
Qwen Code CLI Provider.

Adapter for Qwen Code CLI tool with support for:
- qwen2.5-coder:32b (code-optimized, self-hosted, FREE)
"""

from typing import Optional
import subprocess
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class QwenCodeProvider(BaseProvider):
    """Provider for Qwen Code CLI (self-hosted, free)."""

    def __init__(
        self,
        model: str = "qwen2.5-coder:32b",
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize Qwen Code provider.

        Args:
            model: Model to use
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="Qwen Code CLI",
            command="qwen-code",
            subcommand="ask",
            model=model,
            rate_limit=rate_limit,
        )

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via Qwen Code CLI.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse with result
        """
        start_time = time.time()

        try:
            result = subprocess.run(
                ["qwen-code", "ask", prompt],
                capture_output=True,
                text=True,
                timeout=120,
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
            "busy",
            "try again",
        ]

        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
