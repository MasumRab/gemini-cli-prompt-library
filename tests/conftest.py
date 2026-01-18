"""
Pytest configuration and fixtures for DSPy-HELM tests.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch


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


@pytest.fixture(autouse=True)
def suppress_dspy_imports():
    """Suppress dspy import issues during tests by mocking."""
    with patch.dict("sys.modules", {"dspy": MagicMock(), "dspy.evaluate": MagicMock()}):
        yield


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "real_api: mark test as real API test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Sort tests by module for better organization
    items.sort(key=lambda item: (item.fspath, item.name))


# Error handling for lazy dspy imports
@pytest.fixture(scope="session", autouse=True)
def setup_dspy_mocks():
    """Set up persistent mocks for dspy modules."""
    dspy_mock = MagicMock()
    dspy_mock.settings.configure = MagicMock()

    # Mock common dspy classes
    dspy_mock.Signature = type("Signature", (), {})
    dspy_mock.Module = type("Module", (), {})
    dspy_mock.Example = type("Example", (), {})
    dspy_mock.Prediction = type("Prediction", (), {})

    sys.modules["dspy"] = dspy_mock
    sys.modules["dspy.evaluate"] = MagicMock()
    sys.modules["dspy.teleprompt"] = MagicMock()

    yield dspy_mock

    # Cleanup
    if "dspy" in sys.modules:
        del sys.modules["dspy"]
    if "dspy.evaluate" in sys.modules:
        del sys.modules["dspy.evaluate"]
    if "dspy.teleprompt" in sys.modules:
        del sys.modules["dspy.teleprompt"]
