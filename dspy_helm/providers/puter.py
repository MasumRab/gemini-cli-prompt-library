"""
Puter.js Free Provider.

Adapter for Puter.js API - truly FREE, no API key required!
Access 500+ models including GPT, Claude, Grok, DeepSeek.

https://developer.puter.com/tutorials/free-llm-api/
"""

from typing import Optional
import requests
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class PuterFreeProvider(BaseProvider):
    """Provider for Puter.js API - completely free, no API key needed."""

    # Available free models on Puter.js
    FREE_MODELS = {
        "gpt-5-nano": "GPT-5 Nano (fast, efficient)",
        "claude-sonnet-4": "Claude Sonnet 4 (reasoning)",
        "deepseek-r1": "DeepSeek R1 (complex reasoning)",
        "grok-code": "Grok Code (coding specialized)",
        "gemma-3": "Gemma 3 (multilingual)",
    }

    def __init__(
        self,
        model: str = "gpt-5-nano",
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize Puter.js free provider.

        Args:
            model: Model to use (default: gpt-5-nano)
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="Puter.js Free API",
            command="api",
            subcommand="puter-free",
            model=model,
            rate_limit=rate_limit,
        )
        self.base_url = "https://api.puter.com/v1/chat/completions"
        self.session = requests.Session()
        # Add proper headers to avoid 403
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via Puter.js API (free).

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse with result
        """
        start_time = time.time()

        try:
            response = self.session.post(
                self.base_url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                },
                timeout=60,
            )

            latency = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return ProviderResponse(
                    success=True,
                    content=content,
                    provider=self.name,
                    model=self.model,
                    latency_seconds=latency,
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                return ProviderResponse(
                    success=False,
                    error=error_msg,
                    provider=self.name,
                    model=self.model,
                    latency_seconds=latency,
                )

        except requests.exceptions.Timeout:
            return ProviderResponse(
                success=False,
                error="Request timed out after 60 seconds",
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

    def list_free_models(self) -> list:
        """List all available free models."""
        return list(self.FREE_MODELS.keys())


# Also create a simple helper function for quick testing
def test_puter_free(model: str = "gpt-5-nano") -> bool:
    """
    Quick test of Puter.js free API.

    Args:
        model: Model to test

    Returns:
        True if successful, False otherwise
    """
    provider = PuterFreeProvider(model=model)
    response = provider.call("Say 'Hello from free Puter.js API!' in exactly 5 words.")

    if response.success:
        print(f"✓ {model}: {response.content}")
        return True
    else:
        print(f"✗ {model}: {response.error}")
        return False
