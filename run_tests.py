#!/usr/bin/env python
"""Run tests with proper module mocking to avoid Bus errors."""

import sys
from unittest.mock import MagicMock

# CRITICAL: Mock problematic modules BEFORE pytest loads
_mock_modules = {
    "tokenizers": MagicMock(),
    "litellm": MagicMock(),
    "litellm.utils": MagicMock(),
    "litellm.utils.py.httpx": MagicMock(),
    "litellm.main": MagicMock(),
    "httpx": MagicMock(),
    "httpx._transports": MagicMock(),
    "httpx._transports.default": MagicMock(),
}

for mod_name, mock in _mock_modules.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock

# Now run pytest
import pytest  # noqa: E402

sys.exit(
    pytest.main(
        [
            "tests/",
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
        ]
    )
)
