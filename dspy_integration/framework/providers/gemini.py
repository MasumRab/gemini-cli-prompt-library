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
from ..common import CommonUtils


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
            # Use common utility for subprocess execution
            returncode, stdout, stderr = CommonUtils.execute_subprocess_cmd(
                ["gemini", "ask", prompt], timeout=120
            )

            latency = time.time() - start_time

            if returncode != 0:
                error_output = stderr or stdout
                rate_limited = CommonUtils.is_rate_limited(error_output)

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
                content=stdout.strip(),
                provider=self.name,
                model=self.model,
                latency_seconds=latency,
            )

        except Exception as e:
            return ProviderResponse(
                success=False,
                error=str(e),
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time,
            )
