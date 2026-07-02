"""
HuggingFace Inference API Provider.

Free tier for inference on Hugging Face models.
Works well for code generation and text tasks.

https://huggingface.co/inference-api
"""

import os
from typing import Optional
import requests
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class HuggingFaceProvider(BaseProvider):
    """Provider for HuggingFace Inference API - free tier available."""

    # Free tier models available on HuggingFace
    FREE_MODELS = {
        "meta-llama/Llama-3.2-3B-Instruct": "Llama 3.2 3B (instruct-tuned)",
        "meta-llama/Llama-3.2-1B-Instruct": "Llama 3.2 1B (fast)",
        "microsoft/Phi-3.5-mini-instruct": "Phi-3.5 Mini (efficient)",
        "Qwen/Qwen2.5-Coder-1.5B-Instruct": "Qwen 2.5 Coder 1.5B (code specialized)",
        "deepseek-coder-1.3b-instruct": "DeepSeek Coder 1.3B (code specialized)",
    }

    def __init__(
        self,
        model: str = "meta-llama/Llama-3.2-3B-Instruct",
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize HuggingFace provider.

        Args:
            model: Model to use (default: meta-llama/Llama-3.2-3B-Instruct)
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="HuggingFace Inference API",
            command="api",
            subcommand="huggingface",
            model=model,
            rate_limit=rate_limit,
        )
        self.base_url = "https://api-inference.huggingface.co/models/"
        self.api_key = os.environ.get("HF_API_KEY", "") or os.environ.get(
            "HUGGINGFACE_API_KEY", ""
        )
        self.session = requests.Session()
        headers = {
            "User-Agent": "DSPy-HELM/1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.session.headers.update(headers)

    def is_configured(self) -> bool:
        """Check if HuggingFace API key is configured (optional for free tier)."""
        # Free tier works without API key but has rate limits
        return True  # Always available, optionally with API key for higher limits

    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via HuggingFace Inference API.

        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments

        Returns:
            ProviderResponse with result
        """
        start_time = time.time()

        try:
            # HF uses a different format - inputs field instead of messages
            response = self.session.post(
                f"{self.base_url}{self.model}",
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 1000,
                        "temperature": 0.7,
                        "return_full_text": False,
                    },
                },
                timeout=60,
            )

            latency = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                # HF returns array with generated text
                if isinstance(data, list) and len(data) > 0:
                    content = data[0].get("generated_text", "")
                    # Remove the input prompt from response if included
                    if content.startswith(prompt):
                        content = content[len(prompt) :].strip()
                    return ProviderResponse(
                        success=True,
                        content=content,
                        provider=self.name,
                        model=self.model,
                        latency_seconds=latency,
                    )
                else:
                    return ProviderResponse(
                        success=False,
                        error=f"Unexpected response format: {data}",
                        provider=self.name,
                        model=self.model,
                        latency_seconds=latency,
                    )
            elif response.status_code == 401:
                return ProviderResponse(
                    success=False,
                    error="Model loading. Try again in a few seconds.",
                    provider=self.name,
                    model=self.model,
                    latency_seconds=latency,
                )
            elif response.status_code == 503:
                return ProviderResponse(
                    success=False,
                    error="Model is loading. Please try again later.",
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
def test_huggingface(model: str = "meta-llama/Llama-3.2-3B-Instruct") -> bool:
    """
    Quick test of HuggingFace Inference API.

    Args:
        model: Model to test

    Returns:
        True if successful, False otherwise
    """
    provider = HuggingFaceProvider(model=model)
    response = provider.call("Say 'Hello from HuggingFace API!' in exactly 5 words.")

    if response.success:
        print(f"✓ {model}: {response.content}")
        return True
    else:
        print(f"✗ {model}: {response.error}")
        return False
