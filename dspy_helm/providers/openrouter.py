"""
OpenRouter Provider.

Adapter for OpenRouter API with support for:
- x-ai/grok-4.1-fast:free (primary - Grok, free)
- prime-intellect/intellect-3 (free)
"""

from typing import Optional
import os
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
        Create an OpenRouter (Grok) provider configured with the chosen model, API key, and optional rate limiting.
        
        Parameters:
            model (str): Model identifier to use (default: "x-ai/grok-4.1-fast:free").
            api_key (Optional[str]): OpenRouter API key; if omitted, the value of the
                environment variable OPENROUTER_API_KEY will be used when available.
            rate_limit (Optional[RateLimitConfig]): Rate limiting configuration for requests.
        """
        super().__init__(
            name="OpenRouter (Grok)",
            command="api",
            subcommand="openrouter",
            model=model,
            rate_limit=rate_limit,
        )
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Send a chat prompt to the OpenRouter API and return a ProviderResponse summarizing the outcome.
        
        Sends the prompt as a single user message to the configured model and measures round-trip latency.
        
        Parameters:
            prompt (str): The prompt text to send.
        
        Returns:
            ProviderResponse: On success includes `content` (model output), `provider`, `model`, `latency_seconds`, and `tokens_used` (0 if unavailable). On failure includes `error`, `provider`, and `model`; if the failure is due to rate limiting, `rate_limited` is set to `True`.
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

        except (
            openai.APIConnectionError,
            openai.AuthenticationError,
            openai.APIError,
        ) as e:
            return ProviderResponse(
                success=False,
                error=f"{type(e).__name__}: {str(e)}",
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
        ]

        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
