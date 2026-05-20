"""
Gemini CLI Provider.

Adapter for Gemini CLI tool with support for:
- gemini-1.5-flash (FREE tier)
- gemini-1.5-pro
"""

from dspy_helm.providers.gemini import GeminiProvider

__all__ = ["GeminiProvider"]
