"""
Groq API Provider.

Fast inference API with free tier available.
Uses OpenAI-compatible API format.

https://console.groq.com/
"""

import os
from typing import Optional
import requests
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class GroqProvider(BaseProvider):
    """Provider for Groq API - fast inference with free tier."""

    # Free tier models available on Groq
    FREE_MODELS = {
        "llama-3.3-70b-versatile": "Llama 3.3 70B (general purpose)",
        "llama-3.1-8b-instant": "Llama 3.1 8B (fast, efficient)",
        "gemma-7b-it": "Gemma 7B (Google's model)",
        "mixtral-8x7b-32768": "Mixtral 8x7B (Mixture of experts)",
    }

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize Groq provider.

        Args:
            model: Model to use (default: llama-3.3-70b-versatile)
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="Groq API",
            command="api",
            subcommand="groq",
            model=model,
            rate_limit=rate_limit,
        )
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.api_key = os.environ.get("GROQ_API_KEY", "")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "DSPy-HELM/1.0",
            }
        )

    def is_configured(self) -> bool:
        """Check if Groq API key is configured."""
        return bool(self.api_key)

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via Groq API.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse with result
        """
        start_time = time.time()

        # Check if API key is configured
        if not self.is_configured():
            return ProviderResponse(
                success=False,
                error="GROQ_API_KEY not configured. Set GROQ_API_KEY environment variable.",
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time,
            )

        try:
            response = self.session.post(
                self.base_url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7,
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
            elif response.status_code == 401:
                return ProviderResponse(
                    success=False,
                    error="Invalid API key. Check GROQ_API_KEY environment variable.",
                    provider=self.name,
                    model=self.model,
                    latency_seconds=latency,
                )
            elif response.status_code == 429:
                return ProviderResponse(
                    success=False,
                    error="Rate limit exceeded. Try again later.",
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

    def list_models(self) -> list:
        """List all available free models."""
        return list(self.FREE_MODELS.keys())


# Quick test function
def test_groq(model: str = "llama-3.3-70b-versatile") -> bool:
    """
    Quick test of Groq API.

    Args:
        model: Model to test

    Returns:
        True if successful, False otherwise
    """
    provider = GroqProvider(model=model)
    response = provider.call("Say 'Hello from Groq API!' in exactly 5 words.")

    if response.success:
        print(f"✓ {model}: {response.content}")
        return True
    else:
        print(f"✗ {model}: {response.error}")
        return False
