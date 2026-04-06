"""
Pytest configuration and fixtures for DSPy-HELM tests.
"""

import pytest
import sys
import os  # noqa: F401
from pathlib import Path
from unittest.mock import MagicMock, patch

# CRITICAL: Mock problematic modules BEFORE any other imports
# This must happen at the very beginning to prevent Bus errors with tokenizers
# and litellm issues

# Create a mock for dspy first - before any imports that depend on it
_dspy_mock = MagicMock()
_dspy_mock.settings = MagicMock()
_dspy_mock.settings.lm = None
_dspy_mock.settings.configure = MagicMock()


class MockExample:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def with_inputs(self, *fields):
        return self

    def inputs(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


class MockPrediction:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockField:
    def __init__(self, **kwargs):
        pass


class MockSignature:
    __fields__ = {"code": MockField(), "review": MockField()}


_dspy_mock.Signature = MockSignature
_dspy_mock.Module = type("Module", (), {})
_dspy_mock.Module.__init__ = lambda self: None
_dspy_mock.Module.forward = lambda self, *args, **kwargs: MagicMock()
_dspy_mock.Example = MockExample
_dspy_mock.Prediction = MockPrediction
_dspy_mock.ChainOfThought = MagicMock(return_value=MagicMock())
_dspy_mock.Predict = MagicMock(return_value=MagicMock())
_dspy_mock.CoT = _dspy_mock.ChainOfThought
_dspy_mock.Evaluate = MagicMock()
_dspy_mock.evaluate = MagicMock()
_dspy_mock.teleprompt = MagicMock()
_dspy_mock.teleprompt.BootstrapFewShot = MagicMock()
_dspy_mock.teleprompt.MIPROv2 = MagicMock()
_dspy_mock.functional = MagicMock()
_dspy_mock.InputField = MockField
_dspy_mock.OutputField = MockField

# Insert dspy mock before any other imports
sys.modules["dspy"] = _dspy_mock
sys.modules["dspy.predict"] = MagicMock()
sys.modules["dspy.evaluate"] = MagicMock()
sys.modules["dspy.teleprompt"] = MagicMock()
sys.modules["dspy.functional"] = MagicMock()
sys.modules["dspy.primitives"] = MagicMock()
sys.modules["dspy.primitives.module"] = MagicMock()
sys.modules["dspy.primitives.base_module"] = MagicMock()
sys.modules["dspy.utils"] = MagicMock()
sys.modules["dspy.utils.saving"] = MagicMock()
sys.modules["dspy.streaming"] = MagicMock()
sys.modules["dspy.streaming.messages"] = MagicMock()
sys.modules["dspy.streaming.streamify"] = MagicMock()
sys.modules["dspy.streaming.streaming_listener"] = MagicMock()
sys.modules["dspy.adapters"] = MagicMock()
sys.modules["dspy.adapters.chat_adapter"] = MagicMock()
sys.modules["dspy.clients"] = MagicMock()
sys.modules["dspy.clients.lm"] = MagicMock()
sys.modules["dspy.predict.aggregation"] = MagicMock()
sys.modules["dspy.predict.chain_of_thought"] = MagicMock()
sys.modules["dspy.evaluate.auto_evaluation"] = MagicMock()

_mock_modules = {
    "requests": MagicMock(),
    "tokenizers": MagicMock(),
    "tokenizers.models": MagicMock(),
    "tokenizers.decoders": MagicMock(),
    "tokenizers.normalizers": MagicMock(),
    "tokenizers.pre_tokenizers": MagicMock(),
    "tokenizers.trainers": MagicMock(),
    "tokenizers.implementations": MagicMock(),
    "litellm": MagicMock(),
    "litellm._logging": MagicMock(),
    "litellm.main": MagicMock(),
    "litellm.utils": MagicMock(),
    "litellm.utils.py": MagicMock(),
    "litellm.utils.py.httpx": MagicMock(),
    "litellm.llms": MagicMock(),
    "litellm.llms.custom_httpx": MagicMock(),
    "litellm.completion": MagicMock(),
    "litellm.embedding": MagicMock(),
    "litellm.aiosettings": MagicMock(),
    "httpx": MagicMock(),
    "httpx._client": MagicMock(),
    "httpx._transports": MagicMock(),
    "httpx._transports.default": MagicMock(),
    "httpx._urls": MagicMock(),
    "httpx._auth": MagicMock(),
    "anyio": MagicMock(),
    "jinja2": MagicMock(),
    "yaml": MagicMock(),
    "openai": MagicMock(),
    "openai.types": MagicMock(),
    "openai.types.batch": MagicMock(),
    "openai._models": MagicMock(),
    "openai._compat": MagicMock(),
}

for mod_name, mock in _mock_modules.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_gemini_api_key() -> str:
    """Get Gemini API key from config."""
    config_path = Path.home() / ".config" / "terminal-jarvis" / "credentials.toml"
    if config_path.exists():
        content = config_path.read_text()
        if "GEMINI_API_KEY" in content:
            for line in content.split("\n"):
                if "GEMINI_API_KEY" in line:
                    return line.split("=")[1].strip().strip('"')
    return ""


def get_openrouter_api_key() -> str:
    """Get OpenRouter API key from config."""
    config_path = Path.home() / ".config" / "shai" / "auth.config"
    if config_path.exists():
        content = config_path.read_text()
        for line in content.split("\n"):
            if "sk-" in line and "or-v1" in line:
                return line.strip()
    return ""


# Check available providers
AVAILABLE_PROVIDERS = {
    "gemini": bool(get_gemini_api_key()),
    "openrouter": bool(get_openrouter_api_key()),
    "opencode_zen": True,  # No API key needed
}


@pytest.fixture
def gemini_api_key():
    """Get Gemini API key."""
    return get_gemini_api_key()


@pytest.fixture
def openrouter_api_key():
    """Get OpenRouter API key."""
    return get_openrouter_api_key()


@pytest.fixture
def any_provider_available():
    """Check if any provider is available."""
    return any(AVAILABLE_PROVIDERS.values())


@pytest.fixture
def mock_dspy_settings():
    """Mock dspy settings for tests."""
    with patch("dspy.settings") as mock:
        mock.lm = None
        mock.configure = MagicMock()
        yield mock


@pytest.fixture
def sample_security_review_data():
    """Sample security review test data."""
    return {
        "code": "SELECT * FROM users WHERE name = 'user_input'",
        "expected": "SQL injection",
    }


@pytest.fixture
def sample_unit_test_data():
    """Sample unit test data."""
    return {
        "function": "function add(a, b) { return a + b; }",
        "tests": "Basic, edge, negative cases",
    }


@pytest.fixture
def sample_documentation_data():
    """Sample documentation data."""
    return {
        "project": "A CLI tool for file processing",
        "readme": "installation, usage, examples",
    }


@pytest.fixture
def sample_api_design_data():
    """Sample API design data."""
    return {
        "requirements": "User management system with authentication",
        "design": "POST /users, GET /users/{id}, POST /auth/login",
    }


@pytest.fixture
def mock_provider_response():
    """Create a mock provider response."""
    from dspy_helm.providers.base import ProviderResponse

    return ProviderResponse(
        success=True,
        content="Test response",
        provider="TestProvider",
        model="test-model",
        tokens_used=100,
        latency_seconds=0.5,
    )


@pytest.fixture
def mock_example():
    """Create a mock dspy Example."""

    class MockExample:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def inputs(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

        def with_inputs(self, *fields):
            return self

    return MockExample


@pytest.fixture
def mock_prediction():
    """Create a mock dspy Prediction."""

    class MockPrediction:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    return MockPrediction


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory with sample JSONL files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create sample security review data
    security_data = data_dir / "security_review.jsonl"
    security_data.write_text(
        '{"vars": {"code": "test code", "expected": "test expected"}}\n'
        '{"vars": {"code": "test code 2", "expected": "test expected 2"}}\n'
    )

    # Create sample unit test data
    unit_data = data_dir / "unit_test.jsonl"
    unit_data.write_text(
        '{"input": "function test() {}", "expected_output": "test cases"}\n'
    )

    return data_dir


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "real_api: mark test as real API test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Sort tests by module for better organization
    items.sort(key=lambda item: (item.fspath, item.name))
