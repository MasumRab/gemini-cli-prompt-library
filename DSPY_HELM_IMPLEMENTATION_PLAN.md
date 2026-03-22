# DSPy-HELM Implementation Plan - Complete Details

## Document Overview

This document contains the complete implementation plan for integrating dspy-helm architecture into the gemini-cli-prompt-library project while preserving existing functionality.

## IMPORTANT: Architecture Decision

### Provider Failover Strategy (Rate Limit Rotation)

The system uses **sequential failover** - not parallel execution. When one provider hits a rate limit, it rotates to the next provider in the chain.

**IMPORTANT**: OpenCode CLI uses OpenAI's **FREE tier models** - no cost for any provider!

**Provider Priority Chain:**
| Priority | Provider | CLI Command | Model | Cost |
|----------|----------|-------------|-------|------|
| 1st | OpenCode | `opencode ask` | GPT-4o-mini (FREE tier) | **$0** |
| 2nd | Qwen Code | `qwen-code ask` | Qwen2.5-Coder:32b (self-hosted) | **$0** |
| 3rd | Gemini CLI | `gemini ask` | Gemini 1.5 Flash (FREE tier) | **$0** |

---

## Part 1: Project Structure

### 1.1 New Directory Structure

```
gemini-cli-prompt-library/
├── commands/                         # EXISTING - TOML prompts (30+ files)
├── dspy_integration/                 # EXISTING - Partial DSPy modules
├── dspy_helm/                        # NEW - DSPy-HELM implementation
│   ├── __init__.py
│   ├── version.py
│   ├── config/                       # NEW - Configuration
│   │   ├── __init__.py
│   │   └── providers.yaml            # Provider configuration
│   ├── providers/                    # NEW - Provider abstraction
│   │   ├── __init__.py
│   │   ├── base.py                   # Provider interface
│   │   ├── opencode.py               # OpenCode CLI adapter
│   │   ├── qwen.py                   # Qwen Code CLI adapter
│   │   └── gemini.py                 # Gemini CLI adapter
│   ├── scenarios/
│   │   ├── __init__.py
│   │   ├── base.py                   # BaseScenario, ScenarioRegistry
│   │   ├── security_review.py        # SecurityReviewScenario
│   │   ├── unit_test.py              # UnitTestScenario
│   │   ├── documentation.py          # DocumentationScenario
│   │   └── api_design.py             # APIDesignScenario
│   ├── optimizers/
│   │   ├── __init__.py
│   │   ├── base.py                   # IOptimizer, BaseOptimizer
│   │   ├── mipro_v2.py               # MIPROv2Optimizer
│   │   └── bootstrap.py              # BootstrapFewShot
│   ├── eval/
│   │   ├── __init__.py
│   │   └── evaluate.py               # Evaluator class
│   └── cli.py                        # CLI entry point
├── data/                             # NEW - Test datasets
│   ├── security_review.jsonl
│   ├── unit_test.jsonl
│   ├── documentation.jsonl
│   └── api_design.jsonl
├── agents/                           # NEW - Output directory
│   └── README.md
├── run.sh                            # NEW - Batch runner
├── requirements.txt                  # NEW - Dependencies
└── DSPY_HELM_IMPLEMENTATION_PLAN.md  # This document
```

### 1.2 requirements.txt (NEW)

```txt
# Core dependencies
dspy==3.0.3
datasets==4.1.1
requests==2.32.3
urllib3==2.3.0
cloudpickle==3.1.0

# Optional: For Ollama local inference (if needed later)
# openai>=1.0.0

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

---

## Part 2: Provider Configuration

### 2.1 config/providers.yaml

```yaml
# Provider Configuration for DSPy-HELM
# Uses sequential failover for rate limit rotation

providers:
  # Primary Provider - OpenCode CLI with GPT-4o-mini
  opencode:
    name: "OpenCode CLI"
    command: "opencode"
    subcommand: "ask"
    models:
      default: "gpt-4o-mini"
      available:
        - "gpt-4o-mini"
        - "claude-3-5-sonnet"
        - "deepseek-chat"
    model_mapping:
      gpt-4o-mini: "openai/gpt-4o-mini"
      claude-3-5-sonnet: "anthropic/claude-3-5-sonnet"
      deepseek-chat: "deepseek/deepseek-chat"
    rate_limit:
      enabled: true
      max_retries: 3
      backoff_factor: 1.0
    cost_per_1k_tokens: 0.0  # FREE - uses OpenAI free tier
    priority: 1

  # Secondary Provider - Qwen Code CLI with Qwen-Coder
  qwen:
    name: "Qwen Code CLI"
    command: "qwen-code"
    subcommand: "ask"
    models:
      default: "qwen2.5-coder:32b"
      available:
        - "qwen2.5-coder:32b"
        - "qwen2.5-72b-instruct"
    model_mapping:
      qwen2.5-coder:32b: "qwen/qwen-2.5-coder-32b"
      qwen2.5-72b-instruct: "qwen/qwen-2.5-72b-instruct"
    rate_limit:
      enabled: true
      max_retries: 3
      backoff_factor: 0.5
    cost_per_1k_tokens: 0.0
    priority: 2

  # Tertiary Provider - Gemini CLI with Gemini 1.5 Flash
  gemini:
    name: "Gemini CLI"
    command: "gemini"
    subcommand: "ask"
    models:
      default: "gemini-1.5-flash"
      available:
        - "gemini-1.5-flash"
        - "gemini-1.5-pro"
    model_mapping:
      gemini-1.5-flash: "google/gemini-1.5-flash"
      gemini-1.5-pro: "google/gemini-1.5-pro"
    rate_limit:
      enabled: true
      max_retries: 3
      backoff_factor: 2.0
    cost_per_1k_tokens: 0.0
    priority: 3

# Execution Configuration
execution:
  mode: "sequential"  # Sequential failover, not parallel
  fallback_chain:
    - opencode
    - qwen
    - gemini
  timeout_seconds: 120
  default_provider: opencode

# Logging Configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  log_requests: true
  log_responses: false
```

---

## Part 3: Provider Base Classes

### 3.1 providers/base.py

```python
"""
Base classes for CLI tool providers.

Provides abstraction layer for different CLI tools
following the Strategy pattern for provider rotation.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import time
import logging
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


@dataclass
class ProviderResponse:
    """Response from a provider."""
    success: bool
    content: str = ""
    provider: str = ""
    model: str = ""
    error: Optional[str] = None
    tokens_used: int = 0
    latency_seconds: float = 0.0
    rate_limited: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class RateLimitConfig:
    """Configuration for rate limiting."""
    enabled: bool = True
    max_retries: int = 3
    backoff_factor: float = 1.0
    max_backoff: float = 60.0


class BaseProvider(ABC):
    """Abstract base class for CLI providers."""
    
    def __init__(
        self,
        name: str,
        command: str,
        subcommand: str,
        model: str,
        rate_limit: Optional[RateLimitConfig] = None
    ):
        """
        Initialize provider.
        
        Args:
            name: Provider display name
            command: CLI command to run
            subcommand: CLI subcommand (e.g., "ask")
            model: Default model to use
            rate_limit: Rate limiting configuration
        """
        self.name = name
        self.command = command
        self.subcommand = subcommand
        self.model = model
        self.rate_limit = rate_limit or RateLimitConfig()
        
        self._last_request_time = 0.0
        self._retry_count = 0
    
    @abstractmethod
    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute the CLI command.
        
        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments
        
        Returns:
            ProviderResponse with result or error
        """
        ...
    
    def call(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Call the provider with retry logic for rate limits.
        
        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments
        
        Returns:
            ProviderResponse with result
        """
        if not self.rate_limit.enabled:
            return self._execute_cli(prompt, **kwargs)
        
        max_retries = self.rate_limit.max_retries
        backoff = self.rate_limit.backoff_factor
        
        for attempt in range(max_retries + 1):
            response = self._execute_cli(prompt, **kwargs)
            
            if response.success:
                self._retry_count = 0
                return response
            
            if not response.rate_limited:
                return response
            
            if attempt < max_retries:
                wait_time = min(backoff * (2 ** attempt), self.rate_limit.max_backoff)
                logger.warning(
                    f"Rate limited by {self.name}, retrying in {wait_time}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries exceeded for {self.name}")
                return response
        
        return ProviderResponse(
            success=False,
            error="Max retries exceeded",
            provider=self.name,
            model=self.model
        )
    
    def __repr__(self) -> str:
        return f"{self.name}(model={self.model})"


class ProviderChain:
    """
    Chain of providers with failover support.
    
    Manages rotation through providers when rate limits
    are encountered.
    """
    
    def __init__(self, providers: List[BaseProvider]):
        """
        Initialize provider chain.
        
        Args:
            providers: List of providers in priority order
        """
        self.providers = providers
        self._current_index = 0
    
    def call(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Call providers in sequence with failover.
        
        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments
        
        Returns:
            ProviderResponse from first successful provider
        """
        last_error = None
        
        for provider in self.providers:
            response = provider.call(prompt, **kwargs)
            
            if response.success:
                return response
            
            last_error = response.error
            logger.info(
                f"Provider {provider.name} failed: {response.error}. "
                f"Trying next provider..."
            )
        
        return ProviderResponse(
            success=False,
            error=f"All providers failed: {last_error}",
            provider="none",
            model="none"
        )
    
    def add_provider(self, provider: BaseProvider) -> None:
        """Add provider to chain."""
        self.providers.append(provider)
    
    def set_fallback_order(self, provider_names: List[str]) -> None:
        """
        Reorder providers by name.
        
        Args:
            provider_names: List of provider names in desired order
        """
        name_to_provider = {p.name: p for p in self.providers}
        self.providers = [
            name_to_provider[name] for name in provider_names
            if name in name_to_provider
        ]
```

---

## Part 4: Provider Implementations

### 4.1 providers/opencode.py

```python
"""
OpenCode CLI Provider.

Adapter for OpenCode CLI tool with support for:
- gpt-4o-mini (primary)
- claude-3-5-sonnet
- deepseek-chat
"""

from typing import Optional
import subprocess
import json
import logging
from .base import BaseProvider, ProviderResponse, RateLimitConfig


logger = logging.getLogger(__name__)


class OpenCodeProvider(BaseProvider):
    """Provider for OpenCode CLI."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        rate_limit: Optional[RateLimitConfig] = None
    ):
        """
        Initialize OpenCode provider.
        
        Args:
            model: Model to use (gpt-4o-mini, claude-3-5-sonnet, deepseek-chat)
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="OpenCode CLI",
            command="opencode",
            subcommand="ask",
            model=model,
            rate_limit=rate_limit
        )
    
    def _execute_cli(self, prompt: str, **kwargs) -> ProviderResponse:
        """
        Execute prompt via OpenCode CLI.
        
        Args:
            prompt: Prompt to send
            **kwargs: Additional arguments (ignored)
        
        Returns:
            ProviderResponse with result
        """
        import time
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ["opencode", "ask", prompt],
                capture_output=True,
                text=True,
                timeout=120
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
                    latency_seconds=latency
                )
            
            return ProviderResponse(
                success=True,
                content=result.stdout.strip(),
                provider=self.name,
                model=self.model,
                latency_seconds=latency
            )
            
        except subprocess.TimeoutExpired:
            return ProviderResponse(
                success=False,
                error="Command timed out after 120 seconds",
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time
            )
        
        except Exception as e:
            return ProviderResponse(
                success=False,
                error=str(e),
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time
            )
    
    def _is_rate_limited(self, output: str) -> bool:
        """
        Detect if output indicates rate limiting.
        
        Args:
            output: CLI output or error message
        
        Returns:
            True if rate limited
        """
        rate_limit_indicators = [
            "rate limit",
            "rate_limit",
            "too many requests",
            "429",
            "exceeded quota",
            "capacity",
            "try again later"
        ]
        
        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
```

### 4.2 providers/qwen.py

```python
"""
Qwen Code CLI Provider.

Adapter for Qwen Code CLI tool with support for:
- qwen2.5-coder:32b (primary - code-optimized)
- qwen2.5-72b-instruct
"""

from typing import Optional
import subprocess
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class QwenCodeProvider(BaseProvider):
    """Provider for Qwen Code CLI."""
    
    def __init__(
        self,
        model: str = "qwen2.5-coder:32b",
        rate_limit: Optional[RateLimitConfig] = None
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
            rate_limit=rate_limit
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
                timeout=120
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
                    latency_seconds=latency
                )
            
            return ProviderResponse(
                success=True,
                content=result.stdout.strip(),
                provider=self.name,
                model=self.model,
                latency_seconds=latency
            )
            
        except subprocess.TimeoutExpired:
            return ProviderResponse(
                success=False,
                error="Command timed out after 120 seconds",
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time
            )
        
        except Exception as e:
            return ProviderResponse(
                success=False,
                error=str(e),
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time
            )
    
    def _is_rate_limited(self, output: str) -> bool:
        """Detect rate limiting indicators."""
        rate_limit_indicators = [
            "rate limit",
            "too many requests",
            "429",
            "busy",
            "try again"
        ]
        
        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
```

### 4.3 providers/gemini.py

```python
"""
Gemini CLI Provider.

Adapter for Gemini CLI tool with support for:
- gemini-1.5-flash (primary - free tier generous)
- gemini-1.5-pro
"""

from typing import Optional
import subprocess
import time
from .base import BaseProvider, ProviderResponse, RateLimitConfig


class GeminiProvider(BaseProvider):
    """Provider for Gemini CLI."""
    
    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        rate_limit: Optional[RateLimitConfig] = None
    ):
        """
        Initialize Gemini provider.
        
        Args:
            model: Model to use
            rate_limit: Rate limiting configuration
        """
        super().__init__(
            name="Gemini CLI",
            command="gemini",
            subcommand="ask",
            model=model,
            rate_limit=rate_limit
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
            result = subprocess.run(
                ["gemini", "ask", prompt],
                capture_output=True,
                text=True,
                timeout=120
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
                    latency_seconds=latency
                )
            
            return ProviderResponse(
                success=True,
                content=result.stdout.strip(),
                provider=self.name,
                model=self.model,
                latency_seconds=latency
            )
            
        except subprocess.TimeoutExpired:
            return ProviderResponse(
                success=False,
                error="Command timed out after 120 seconds",
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time
            )
        
        except Exception as e:
            return ProviderResponse(
                success=False,
                error=str(e),
                provider=self.name,
                model=self.model,
                latency_seconds=time.time() - start_time
            )
    
    def _is_rate_limited(self, output: str) -> bool:
        """Detect rate limiting indicators."""
        rate_limit_indicators = [
            "rate limit",
            "too many requests",
            "429",
            "quota exceeded",
            "user rate limit"
        ]
        
        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
```

### 4.4 providers/__init__.py

```python
"""
Provider module for CLI tool adapters.

Provides unified interface for:
- OpenCode CLI (gpt-4o-mini)
- Qwen Code CLI (qwen2.5-coder:32b)
- Gemini CLI (gemini-1.5-flash)
"""

from .base import BaseProvider, ProviderResponse, RateLimitConfig, ProviderChain
from .opencode import OpenCodeProvider
from .qwen import QwenCodeProvider
from .gemini import GeminiProvider


def create_provider_chain() -> ProviderChain:
    """
    Create provider chain with default providers.
    
    Order: OpenCode → Qwen → Gemini (failover priority)
    
    Returns:
        ProviderChain with all providers configured
    """
    providers = [
        OpenCodeProvider(
            model="gpt-4o-mini",
            rate_limit=RateLimitConfig(
                enabled=True,
                max_retries=3,
                backoff_factor=1.0
            )
        ),
        QwenCodeProvider(
            model="qwen2.5-coder:32b",
            rate_limit=RateLimitConfig(
                enabled=True,
                max_retries=3,
                backoff_factor=0.5
            )
        ),
        GeminiProvider(
            model="gemini-1.5-flash",
            rate_limit=RateLimitConfig(
                enabled=True,
                max_retries=3,
                backoff_factor=2.0
            )
        )
    ]
    
    return ProviderChain(providers)


def get_default_provider() -> OpenCodeProvider:
    """Get the default (primary) provider."""
    return OpenCodeProvider(
        model="gpt-4o-mini",
        rate_limit=RateLimitConfig(
            enabled=True,
            max_retries=3,
            backoff_factor=1.0
        )
    )


__all__ = [
    "BaseProvider",
    "ProviderResponse", 
    "RateLimitConfig",
    "ProviderChain",
    "OpenCodeProvider",
    "QwenCodeProvider",
    "GeminiProvider",
    "create_provider_chain",
    "get_default_provider"
]
```

---

## Part 5: Base Classes (SOLID Compliant)

### 5.1 scenarios/base.py

```python
"""
Base classes for DSPy-HELM scenarios.

This module provides the abstract base class and registry pattern
for implementing scenarios following SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Type, Dict, Any, Optional
import random
import dspy
from pathlib import Path


class BaseScenario(ABC):
    """
    Abstract base class for all evaluation scenarios.
    """
    
    INPUT_FIELDS: List[str] = []
    OUTPUT_FIELDS: List[str] = []
    DEFAULT_SPLIT_RATIO: float = 0.8
    MIN_TRAIN_SIZE: int = 5
    MIN_VAL_SIZE: int = 3
    
    def __init__(self, test_size: float = 0.2, seed: int = 42):
        self.test_size = test_size
        self.seed = seed
        random.seed(seed)
    
    def load_data(self) -> Tuple[List[dspy.Example], List[dspy.Example]]:
        """Load and split dataset into train/validation sets."""
        raw_data = self._load_raw_data()
        
        if len(raw_data) < self.MIN_TRAIN_SIZE + self.MIN_VAL_SIZE:
            raise ValueError(
                f"Insufficient data: need at least {self.MIN_TRAIN_SIZE + self.MIN_VAL_SIZE} "
                f"examples, got {len(raw_data)}"
            )
        
        train_data, val_data = self._split_data(raw_data)
        
        return (
            self._to_dspy_examples(train_data),
            self._to_dspy_examples(val_data)
        )
    
    @abstractmethod
    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load raw data from source."""
        ...
    
    def _split_data(
        self, 
        data: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Split data into train and validation sets."""
        split_idx = max(
            self.MIN_TRAIN_SIZE,
            min(
                len(data) - self.MIN_VAL_SIZE,
                int(len(data) * (1 - self.test_size))
            )
        )
        
        train_data = data[:split_idx]
        val_data = data[split_idx:]
        
        return train_data, val_data
    
    def _to_dspy_examples(
        self, 
        data: List[Dict[str, Any]]
    ) -> List[dspy.Example]:
        """Convert data dictionaries to dspy.Example objects."""
        examples = []
        for row in data:
            example = dspy.Example(**row)
            if self.INPUT_FIELDS:
                example = example.with_inputs(*self.INPUT_FIELDS)
            examples.append(example)
        return examples
    
    @abstractmethod
    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Convert a data row to a prompt string."""
        ...
    
    @abstractmethod
    def metric(
        self, 
        example: dspy.Example, 
        pred: dspy.Prediction, 
        trace: Optional[Any] = None
    ) -> float:
        """Evaluate prediction against ground truth."""
        ...
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(test_size={self.test_size}, seed={self.seed})"


class ScenarioRegistry:
    """Registry for scenario classes (Open/Closed Principle)."""
    
    _scenarios: Dict[str, Type[BaseScenario]] = {}
    
    @classmethod
    def register(cls, name: str) -> callable:
        """Decorator to register a scenario class."""
        def decorator(scenario_class: Type[BaseScenario]) -> Type[BaseScenario]:
            if not issubclass(scenario_class, BaseScenario):
                raise TypeError(
                    f"{scenario_class.__name__} must be a subclass of BaseScenario"
                )
            cls._scenarios[name] = scenario_class
            return scenario_class
        return decorator
    
    @classmethod
    def get(cls, name: str) -> Type[BaseScenario]:
        """Get a scenario class by name."""
        if name not in cls._scenarios:
            available = ", ".join(cls._scenarios.keys())
            raise ValueError(
                f"Unknown scenario: '{name}'. Available scenarios: {available}"
            )
        return cls._scenarios[name]
    
    @classmethod
    def list(cls) -> List[str]:
        """List all registered scenarios."""
        return list(cls._scenarios.keys())
```

---

## Part 6: Scenario Implementations

### 6.1 scenarios/security_review.py

```python
"""
Security Code Review Scenario.

Maps to: commands/code-review/security.toml
Category: Code Review & Analysis
"""

from typing import List, Dict, Any
import dspy
from .base import BaseScenario, ScenarioRegistry


@ScenarioRegistry.register("security_review")
class SecurityReviewScenario(BaseScenario):
    """
    Scenario for evaluating security code review prompts.
    """
    
    INPUT_FIELDS = ["code"]
    OUTPUT_FIELDS = ["review"]
    
    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load security review test cases."""
        return [
            {
                "code": "SELECT * FROM users WHERE name = '" + user_input + "'",
                "expected": "SQL injection vulnerability detected. Use parameterized queries."
            },
            {
                "code": "const apiKey = 'sk-12345abcdef';",
                "expected": "Hardcoded API key detected. Use environment variables."
            },
            {
                "code": "function checkAuth(req) { return true; }",
                "expected": "Missing authentication check. Implement proper auth verification."
            },
            {
                "code": "crypto.createHash('md5').update(password).digest('hex')",
                "expected": "MD5 is cryptographically broken. Use SHA-256 or bcrypt."
            },
            {
                "code": "fs.readFileSync(userFile, 'utf8');",
                "expected": "Path traversal risk. Validate and sanitize file paths."
            },
            {
                "code": "eval(userInput);",
                "expected": "Dangerous eval() usage. Avoid dynamic code execution."
            },
            {
                "code": "document.innerHTML = userContent;",
                "expected": "XSS vulnerability. Use textContent or sanitized HTML."
            },
            {
                "code": "process.env.API_KEY in code",
                "expected": "Secret in environment. Use secrets management."
            },
            {
                "code": "if (user.isAdmin) { grantAccess(); }",
                "expected": "Insecure direct reference. Verify admin status server-side."
            },
            {
                "code": "jwt.sign({user: id}, null);",
                "expected": "JWT without expiration. Add exp claim."
            },
            {
                "code": "os.system('rm -rf ' + user_input)",
                "expected": "Command injection risk. Never pass user input to system()."
            },
            {
                "code": "new FileReader(userFile).readAsText(file)",
                "expected": "XXE vulnerability. Disable external entity parsing."
            },
            {
                "code": "requests.get(user_url)",
                "expected": "SSRF vulnerability. Validate and whitelist URLs."
            },
            {
                "code": "password.length > 6",
                "expected": "Weak password policy. Require stronger validation."
            },
            {
                "code": "if (user.admin) { showAdminPanel(); }",
                "expected": "Insecure client-side check. Verify server-side."
            },
            {
                "code": "sessionStorage.setItem('token', jwt)",
                "expected": "Token in localStorage. Use httpOnly cookies."
            },
            {
                "code": "buffer.write(user_data)",
                "expected": "Buffer overflow risk. Validate input length."
            },
            {
                "code": "String.format('SELECT * FROM %s', table_name)",
                "expected": "SQL injection via table name. Whitelist table names."
            },
            {
                "code": "XMLParser.parse(user_xml)",
                "expected": "XXE injection. Use safe XML parser configuration."
            },
            {
                "code": "Math.random() * 1000",
                "expected": "Insecure random. Use cryptographically secure RNG."
            }
        ]
    
    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Create prompt for security review."""
        return f"""# Security Code Review

Please perform a comprehensive security analysis of the following code:

```
{row['code']}
```

## Analysis Framework

### 1. Vulnerability Identification
Identify all security issues present in the code.

### 2. Severity Assessment
Rate each vulnerability:
- Critical: Immediate action required
- High: Significant risk
- Medium: Moderate concern
- Low: Minor improvement

### 3. Remediation
Provide specific, actionable recommendations for each issue.

### 4. Secure Alternative
Show how the code should be written securely.

## Output Format

For each vulnerability found:
- **Issue**: [Description]
- **Severity**: [Critical/High/Medium/Low]
- **Fix**: [Recommendation]
- **Example**: [Secure code alternative]

If no issues found, state: "No security vulnerabilities detected."
"""
    
    def metric(
        self,
        example: dspy.Example,
        pred: dspy.Prediction,
        trace=None
    ) -> float:
        """Evaluate security review quality."""
        import dspy.evaluate
        
        score = dspy.evaluate.answer_exact_match(example, pred, trace)
        
        if score == 0.0:
            expected_lower = example.expected.lower()
            pred_lower = str(pred.review).lower()
            
            vulnerability_terms = [
                "sql injection", "xss", "csrf", "authentication",
                "authorization", "injection", "cryptograph",
                "hardcoded", "secret", "vulnerability"
            ]
            
            matches = sum(
                1 for term in vulnerability_terms
                if term in pred_lower
            )
            
            score = min(matches / 3, 1.0)
        
        return score
```

---

### 6.2 scenarios/unit_test.py

```python
"""
Unit Test Generation Scenario.

Maps to: commands/testing/generate-unit-tests.toml
Category: Testing
"""

from typing import List, Dict, Any
from .base import BaseScenario, ScenarioRegistry


@ScenarioRegistry.register("unit_test")
class UnitTestScenario(BaseScenario):
    """Scenario for evaluating unit test generation prompts."""
    
    INPUT_FIELDS = ["function"]
    OUTPUT_FIELDS = ["tests"]
    
    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load unit test generation test cases."""
        return [
            {"function": "function add(a, b) { return a + b; }", "tests": "Basic, edge cases, negative, decimals"},
            {"function": "function validateEmail(email) { return email.includes('@'); }", "tests": "Valid, invalid, empty, edge"},
            {"function": "async function fetchUser(id) { return await db.get(id); }", "tests": "Success, not found, error, timeout"},
            {"function": "function factorial(n) { if (n <= 1) return 1; return n * factorial(n - 1); }", "tests": "Base, recursive, negative, zero"},
            {"function": "function sortArray(arr) { return arr.sort(); }", "tests": "Ascending, descending, numbers, strings, empty"},
            {"function": "class BankAccount { constructor(balance) { this.balance = balance; } }", "tests": "Initial, deposit, negative, large"},
            {"function": "function parseJSON(str) { return JSON.parse(str); }", "tests": "Valid, invalid, empty, type"},
            {"function": "function debounce(fn, delay) { /* impl */ }", "tests": "Once, multiple, delay accuracy"},
            {"function": "function binarySearch(arr, target) { /* impl */ }", "tests": "Found start, found end, not found, empty"},
            {"function": "function formatCurrency(amount) { return '$' + amount.toFixed(2); }", "tests": "Whole, decimal, zero, negative, large"},
            {"function": "function isPalindrome(str) { return str === str.reverse(); }", "tests": "Odd, even, single char, empty, palindrome, not"},
            {"function": "function capitalize(str) { return str[0].toUpperCase() + str.slice(1); }", "tests": "Normal, empty, single char, unicode"},
            {"function": "function chunkArray(arr, size) { /* impl */ }", "tests": "Exact divide, not exact, empty, single"},
            {"function": "function throttle(fn, delay) { /* impl */ }", "tests": "First call, trailing, multiple rapid"},
            {"function": "function deepClone(obj) { return JSON.parse(JSON.stringify(obj)); }", "tests": "Nested, circular, date, function"},
            {"function": "function groupBy(arr, key) { /* impl */ }", "tests": "Multiple groups, empty, single item"},
            {"function": "function unique(arr) { return [...new Set(arr)]; }", "tests": "Duplicates, empty, single type, mixed"},
            {"function": "function sum(arr) { return arr.reduce((a, b) => a + b, 0); }", "tests": "Empty, single, negative, decimals"},
            {"function": "function shuffle(arr) { return arr.sort(() => Math.random() - 0.5); }", "tests": "Distribution, in-place, empty"},
            {"function": "function retry(fn, maxAttempts) { /* impl */ }", "tests": "Success first, success after retries, always fail"}
        ]
    
    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Create prompt for unit test generation."""
        return f"""# Unit Test Generation

Generate comprehensive unit tests for the following code:

```
{row['function']}
```

## Test Requirements

### 1. Test Categories

#### Happy Path Tests
- Valid inputs with expected outputs
- Typical use cases

#### Edge Cases
- Empty inputs (null, undefined, empty string, empty array)
- Zero values
- Negative numbers
- Maximum/minimum values
- Single element collections

#### Error Cases
- Invalid inputs
- Type mismatches
- Out of range values
- Exception scenarios

#### Boundary Conditions
- First and last elements
- Off-by-one scenarios
- Limits and thresholds

### 2. Test Framework

Use Jest for JavaScript/TypeScript, pytest for Python.

### 3. Test Structure (AAA Pattern)
- **Arrange**: Set up test data
- **Act**: Execute function
- **Assert**: Verify results

### 4. Output Format

Provide production-ready test code with:
1. Framework declaration
2. All test cases with descriptions
3. Clear assertions
4. Edge case coverage comments
"""
    
    def metric(self, example: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
        """Evaluate unit test generation quality."""
        import dspy.evaluate
        return dspy.evaluate.answer_exact_match(example, pred, trace)
```

---

### 6.3 scenarios/documentation.py

```python
"""
Documentation Generation Scenario.

Maps to: commands/docs/write-readme.toml
Category: Documentation
"""

from typing import List, Dict, Any
from .base import BaseScenario, ScenarioRegistry


@ScenarioRegistry.register("documentation")
class DocumentationScenario(BaseScenario):
    """Scenario for evaluating documentation generation prompts."""
    
    INPUT_FIELDS = ["project"]
    OUTPUT_FIELDS = ["readme"]
    
    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load documentation generation test cases."""
        return [
            {"project": "A CLI tool for file processing that converts images to PNG", "readme": "installation, usage, examples, features, configuration"},
            {"project": "REST API for blog posts with users and comments", "readme": "endpoints, authentication, models, examples"},
            {"project": "Python library for HTTP requests with caching", "readme": "installation, quick start, api_reference, examples"},
            {"project": "Node.js authentication service with JWT", "readme": "setup, usage, configuration, security considerations"},
            {"project": "Database migration tool for PostgreSQL", "readme": "requirements, installation, commands, examples"},
            {"project": "React component library for data visualization", "readme": "getting started, components, props, examples"},
            {"project": "Go microservice template with Docker", "readme": "structure, building, running, deployment"},
            {"project": "Machine learning pipeline for text classification", "readme": "requirements, training, inference, evaluation"},
            {"project": "Chrome extension for tab management", "readme": "installation, usage, permissions, troubleshooting"},
            {"project": "Static site generator with markdown support", "readme": "quick start, configuration, themes, deployment"},
            {"project": "GraphQL API server with authentication", "readme": "schema, resolvers, auth, examples"},
            {"project": "Redis caching layer for Node.js", "readme": "installation, usage, configuration, patterns"},
            {"project": "Kubernetes operator for database management", "readme": "architecture, installation, custom resources, examples"},
            {"project": "Desktop app for API testing with Vue 3", "readme": "architecture, installation, features, configuration"},
            {"project": "CI/CD pipeline generator for GitHub Actions", "readme": "templates, customization, examples, best practices"},
            {"project": "Real-time collaboration library with WebSockets", "readme": "architecture, usage, events, examples"},
            {"project": "Payment processing SDK with Stripe integration", "readme": "setup, usage, webhooks, error handling"},
            {"project": "Code search tool with regex support", "readme": "installation, usage, patterns, performance"},
            {"project": "Config management system with validation", "readme": "schema, validation, migration, examples"},
            {"project": "Event sourcing library for domain-driven design", "readme": "concepts, usage, commands, queries"}
        ]
    
    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Create prompt for documentation generation."""
        return f"""# README Generation

Create a comprehensive README.md for the following project:

```
{row['project']}
```

## Required Sections

### 1. Project Title & Badges
- Clear, descriptive title
- Build status, version, license badges

### 2. Description
- What the project does
- Why it exists (problem solved)
- Key features (3-5 bullet points)

### 3. Installation
- Prerequisites
- Step-by-step instructions
- Platform-specific notes

### 4. Quick Start
- Minimal working example
- Common use cases

### 5. Usage
- Detailed examples
- Configuration options

### 6. API Documentation (if applicable)
- Key functions/methods
- Parameters and return values

### 7. Contributing
- How to contribute
- Code of conduct

### 8. License
- License type
- Copyright notice

## Output Format

Generate complete, production-ready README.md content in Markdown format.
"""
    
    def metric(self, example: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
        """Evaluate documentation quality."""
        import dspy.evaluate
        return dspy.evaluate.answer_exact_match(example, pred, trace)
```

---

### 6.4 scenarios/api_design.py

```python
"""
API Design Scenario.

Maps to: commands/architecture/design-api.toml
Category: Architecture & Design
"""

from typing import List, Dict, Any
from .base import BaseScenario, ScenarioRegistry


@ScenarioRegistry.register("api_design")
class APIDesignScenario(BaseScenario):
    """Scenario for evaluating API design prompts."""
    
    INPUT_FIELDS = ["requirements"]
    OUTPUT_FIELDS = ["design"]
    
    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load API design test cases."""
        return [
            {"requirements": "User management system with authentication", "design": "POST /users, GET /users/{id}, POST /auth/login, POST /auth/logout"},
            {"requirements": "E-commerce with products, orders, payments", "design": "Products CRUD, Orders CRUD, Payment endpoint, Cart endpoints"},
            {"requirements": "Blog platform with posts, comments, users", "design": "Posts CRUD, Comments CRUD, Users CRUD, Auth endpoints"},
            {"requirements": "File storage system with sharing", "design": "Files CRUD, Folders CRUD, Share endpoints, Download"},
            {"requirements": "Notification system with preferences", "design": "Notifications CRUD, Preferences CRUD, Subscribe endpoint"},
            {"requirements": "Real-time chat application", "design": "Messages CRUD, Channels CRUD, Presence, Typing indicators"},
            {"requirements": "Analytics dashboard with reports", "design": "Reports CRUD, Metrics endpoints, Export endpoints"},
            {"requirements": "Search engine with filters", "design": "Search endpoint, Filters CRUD, Suggestions endpoint"},
            {"requirements": "Booking system with availability", "design": "Bookings CRUD, Availability endpoint, Calendar"},
            {"requirements": "Inventory management system", "design": "Items CRUD, Stock endpoints, Suppliers CRUD, Alerts"},
            {"requirements": "Task management with teams", "design": "Tasks CRUD, Teams CRUD, Assignments, Notifications"},
            {"requirements": "Content management with versioning", "design": "Content CRUD, Versions, Publishing, Archives"},
            {"requirements": "Subscription billing with plans", "design": "Plans CRUD, Subscriptions CRUD, Invoices, Webhooks"},
            {"requirements": "Multi-tenant forum system", "design": "Forums CRUD, Posts CRUD, Moderation, Search"},
            {"requirements": "Device management IoT platform", "design": "Devices CRUD, Telemetry, Commands, Firmware"},
            {"requirements": "Document collaboration with comments", "design": "Documents CRUD, Comments, Versions, Sharing"},
            {"requirements": "Location services with geofencing", "design": "Locations CRUD, Geofences, Tracking, Alerts"},
            {"requirements": "Email marketing platform", "design": "Campaigns CRUD, Templates, Lists, Analytics"},
            {"requirements": "Help desk ticketing system", "design": "Tickets CRUD, Comments, Tags, Assignment rules"},
            {"requirements": "Social feed with recommendations", "design": "Posts CRUD, Feed generation, Follows, Likes"}
        ]
    
    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Create prompt for API design."""
        return f"""# RESTful API Design

Design a comprehensive RESTful API for the following requirements:

```
{row['requirements']}
```

## API Design Requirements

### 1. Resource Modeling
- Identify main entities
- Define relationships
- Plan operations

### 2. HTTP Methods
- GET: Retrieve
- POST: Create
- PUT: Full update
- PATCH: Partial update
- DELETE: Remove

### 3. URL Structure
- Use nouns, not verbs
- Use plural forms
- Limit nesting to 2 levels
- Use kebab-case

### 4. Query Parameters
- Filtering: ?status=active
- Sorting: ?sort=created_at:desc
- Pagination: ?page=2&limit=20
- Field selection: ?fields=id,name

### 5. Response Format

```json
{{
  "data": {{...}},
  "meta": {{
    "pagination": {{...}},
    "request_id": "..."
  }}
}}
```

### 6. Status Codes
- 200: OK
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Output Format

Provide:
1. **API Overview**: Base URL, authentication, version
2. **Endpoints Table**: Method, Path, Description
3. **Detailed Specs**: For each endpoint
4. **Request/Response Examples**
5. **Error Handling Guide**
"""
    
    def metric(self, example: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
        """Evaluate API design quality."""
        import dspy.evaluate
        return dspy.evaluate.answer_exact_match(example, pred, trace)
```

---

## Part 7: Optimizer Implementations

### 7.1 optimizers/base.py

```python
"""
Base classes for DSPy optimizers.
"""

from abc import ABC, abstractmethod
from typing import List, Protocol, Type
import dspy


class IOptimizer(Protocol):
    """Optimizer interface."""
    
    @abstractmethod
    def compile(
        self,
        program: dspy.Module,
        trainset: List[dspy.Example],
        valset: List[dspy.Example]
    ) -> dspy.Module:
        ...


class BaseOptimizer(ABC):
    """Abstract base class for optimizers."""
    
    def __init__(
        self,
        metric,
        max_bootstrapped_demos: int = 3,
        max_labeled_demos: int = 3,
        num_threads: int = 16
    ):
        self.metric = metric
        self.max_bootstrapped_demos = max_bootstrapped_demos
        self.max_labeled_demos = max_labeled_demos
        self.num_threads = num_threads
    
    @abstractmethod
    def _create_teleprompter(self):
        ...
    
    def compile(
        self,
        program: dspy.Module,
        trainset: List[dspy.Example],
        valset: List[dspy.Example]
    ) -> dspy.Module:
        teleprompter = self._create_teleprompter()
        return teleprompter.compile(program, trainset=trainset, valset=valset)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(max_bootstrapped={self.max_bootstrapped_demos}, max_labeled={self.max_labeled_demos})"


class OptimizerRegistry:
    """Registry for optimizer classes."""
    
    _optimizers: dict = {}
    
    @classmethod
    def register(cls, name: str):
        def decorator(optimizer_class: Type[BaseOptimizer]):
            cls._optimizers[name] = optimizer_class
            return optimizer_class
        return decorator
    
    @classmethod
    def create(cls, name: str, metric=None, **kwargs) -> BaseOptimizer:
        if name not in cls._optimizers:
            available = ", ".join(cls._optimizers.keys())
            raise ValueError(f"Unknown optimizer: '{name}'. Available: {available}")
        return cls._optimizers[name](metric=metric, **kwargs)
    
    @classmethod
    def list(cls) -> List[str]:
        return list(cls._optimizers.keys())
```

### 7.2 optimizers/mipro_v2.py

```python
"""
MIPROv2 Optimizer Implementation.
"""

from .base import BaseOptimizer, OptimizerRegistry
from dspy.teleprompt import MIPROv2


@OptimizerRegistry.register("MIPROv2")
class MIPROv2Optimizer(BaseOptimizer):
    """MIPROv2 optimizer for prompt optimization."""
    
    def __init__(
        self,
        metric,
        max_bootstrapped_demos: int = 3,
        max_labeled_demos: int = 3,
        num_threads: int = 16,
        auto: str = "light",
        prompt_model=None,
        task_model=None
    ):
        super().__init__(
            metric=metric,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos,
            num_threads=num_threads
        )
        self.auto = auto
        self.prompt_model = prompt_model
        self.task_model = task_model
    
    def _create_teleprompter(self) -> MIPROv2:
        return MIPROv2(
            metric=self.metric,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
            auto=self.auto,
            prompt_model=self.prompt_model,
            task_model=self.task_model,
            num_threads=self.num_threads
        )
    
    def compile(self, program, trainset, valset):
        import dspy
        
        if not dspy.settings.lm:
            raise RuntimeError(
                "No LM configured. Call dspy.configure(lm=...) first."
            )
        
        teleprompter = self._create_teleprompter()
        return teleprompter.compile(program, trainset=trainset, valset=valset)
```

### 7.3 optimizers/bootstrap.py

```python
"""
BootstrapFewShot Optimizers.
"""

from .base import BaseOptimizer, OptimizerRegistry
from dspy.teleprompt import BootstrapFewShot, BootstrapFewShotWithRandomSearch


@OptimizerRegistry.register("BootstrapFewShot")
class BootstrapFewShotOptimizer(BaseOptimizer):
    """BootstrapFewShot optimizer."""
    
    def _create_teleprompter(self) -> BootstrapFewShot:
        return BootstrapFewShot(
            metric=self.metric,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
            num_threads=self.num_threads
        )


@OptimizerRegistry.register("BootstrapFewShotWithRandomSearch")
class BootstrapFewShotRandomSearchOptimizer(BaseOptimizer):
    """BootstrapFewShot with Random Search optimizer."""
    
    def __init__(
        self,
        metric,
        max_bootstrapped_demos: int = 3,
        max_labeled_demos: int = 3,
        num_threads: int = 16,
        num_candidate_programs: int = 10
    ):
        super().__init__(
            metric=metric,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos,
            num_threads=num_threads
        )
        self.num_candidate_programs = num_candidate_programs
    
    def _create_teleprompter(self) -> BootstrapFewShotWithRandomSearch:
        return BootstrapFewShotWithRandomSearch(
            metric=self.metric,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
            num_candidate_programs=self.num_candidate_programs,
            num_threads=self.num_threads
        )
```

---

## Part 8: Evaluation Framework

### 8.1 eval/evaluate.py

```python
"""
Evaluation harness for DSPy programs.
"""

from typing import List, Callable, Dict, Any
import json
from pathlib import Path
import dspy


class Evaluator:
    """Evaluation harness for DSPy programs."""
    
    def __init__(
        self,
        metric: Callable,
        num_threads: int = 16,
        display_progress: bool = True,
        display_table: int = 0
    ):
        self.metric = metric
        self.num_threads = num_threads
        self.display_progress = display_progress
        self.display_table = display_table
        
        self._evaluator = dspy.Evaluate(
            devset=None,
            metric=metric,
            num_threads=num_threads,
            display_progress=display_progress,
            display_table=display_table
        )
    
    def evaluate(
        self,
        program: dspy.Module,
        devset: List[dspy.Example],
        return_outputs: bool = False
    ) -> Dict[str, Any]:
        """Evaluate a program on a dataset."""
        self._evaluator.devset = devset
        
        if return_outputs:
            from dspy.utils.parallelizer import ParallelExecutor
            
            results = []
            executor = ParallelExecutor(num_threads=self.num_threads)
            
            def process_item(example):
                try:
                    pred = program(**example.inputs())
                    score = self.metric(example, pred)
                    return (example, pred, score)
                except Exception as e:
                    return (example, None, 0.0)
            
            raw_results = executor.execute(process_item, devset)
            
            total_score = 0.0
            for example, pred, score in raw_results:
                if score is None:
                    score = 0.0
                total_score += score
                results.append({
                    "example": dict(example),
                    "prediction": dict(pred) if pred else None,
                    "score": score
                })
            
            avg_score = total_score / len(devset) if devset else 0.0
            
            return {
                "score": avg_score,
                "count": len(devset),
                "outputs": results
            }
        else:
            avg_score = self._evaluator(program)
            return {
                "score": avg_score,
                "count": len(devset)
            }
    
    def export_results(self, results: Dict[str, Any], output_path: Path) -> None:
        """Export evaluation results to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Results exported to: {output_path}")
```

---

## Part 9: CLI Entry Point

### 9.1 cli.py

```python
#!/usr/bin/env python3
"""
DSPy-HELM CLI Entry Point.

Usage:
    python -m dspy_helm.cli --scenario security_review --optimizer MIPROv2
    python -m dspy_helm.cli --scenario unit_test --evaluate-only
    python -m dspy_helm.cli --list-scenarios
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import dspy
from providers import create_provider_chain


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="DSPy-HELM: Evaluation and Optimization Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  List available scenarios:
    python -m dspy_helm.cli --list-scenarios
  
  Evaluate a scenario:
    python -m dspy_helm.cli --scenario security_review --evaluate-only
  
  Optimize with MIPROv2:
    python -m dspy_helm.cli --scenario security_review --optimizer MIPROv2
  
  Use specific provider:
    python -m dspy_helm.cli --scenario unit_test --provider qwen
        """
    )
    
    parser.add_argument("--scenario", help="Scenario name to run")
    parser.add_argument(
        "--optimizer",
        default="MIPROv2",
        choices=["MIPROv2", "BootstrapFewShot", "BootstrapFewShotWithRandomSearch"],
        help="Optimizer to use (default: MIPROv2)"
    )
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "opencode", "qwen", "gemini"],
        help="Provider to use (default: auto - uses failover chain)"
    )
    parser.add_argument(
        "--model",
        default="auto",
        help="Model to use (default: auto - uses provider default)"
    )
    parser.add_argument(
        "--evaluate-only",
        action="store_true",
        help="Only evaluate, don't optimize"
    )
    parser.add_argument(
        "--output",
        default="agents",
        help="Output directory for results (default: agents)"
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="List available scenarios and exit"
    )
    parser.add_argument(
        "--list-optimizers",
        action="store_true",
        help="List available optimizers and exit"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser


def configure_lm_from_provider(provider_name: str, model: str) -> None:
    """Configure DSPy LM from provider."""
    if provider_name == "opencode":
        if model == "auto":
            model = "gpt-4o-mini"
        dspy.configure(lm=dspy.OpenAI(model=model))
    elif provider_name == "qwen":
        if model == "auto":
            model = "qwen2.5-coder:32b"
        dspy.configure(lm=dspy.OpenAI(model=model, api_key="not-needed", base_url="http://localhost:8000/v1"))
    elif provider_name == "gemini":
        if model == "auto":
            model = "gemini-1.5-flash"
        dspy.configure(lm=dspy.Google(model=model))
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def run_pipeline(
    scenario_name: str,
    optimizer_name: str,
    provider_name: str,
    model_name: str,
    output_dir: str,
    evaluate_only: bool = False,
    verbose: bool = False
) -> None:
    """Run the evaluation/optimization pipeline."""
    from scenarios import ScenarioRegistry
    from optimizers import OptimizerRegistry
    from eval import Evaluator
    
    if verbose:
        print(f"Loading scenario: {scenario_name}")
    
    scenario_class = ScenarioRegistry.get(scenario_name)
    scenario = scenario_class()
    trainset, valset = scenario.load_data()
    
    if verbose:
        print(f"Train size: {len(trainset)}, Val size: {len(valset)}")
    
    from dspy_integration.modules import get_module_for_scenario
    program = get_module_for_scenario(scenario_name)
    
    if provider_name != "auto" or model_name != "auto":
        configure_lm_from_provider(provider_name, model_name)
    
    if evaluate_only:
        evaluator = Evaluator(metric=scenario.metric)
        results = evaluator.evaluate(program, valset)
        print(f"Evaluation Score: {results['score']:.2%}")
        
        output_path = Path(output_dir) / scenario_name / "evaluation.json"
        evaluator.export_results(results, output_path)
    else:
        from dspy_helm import OptimizationPipeline
        pipeline = OptimizationPipeline(
            scenario=scenario,
            optimizer_name=optimizer_name
        )
        
        optimized = pipeline.run(trainset, valset)
        
        evaluator = Evaluator(metric=scenario.metric)
        results = evaluator.evaluate(optimized, valset)
        print(f"Optimized Score: {results['score']:.2%}")
        
        output_path = Path(output_dir) / scenario_name / model_name.replace("/", "_")
        output_path.mkdir(parents=True, exist_ok=True)
        optimized.save(output_path / f"{optimizer_name}.json")
        print(f"Optimized program saved to: {output_path}")


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.list_scenarios:
        from scenarios import ScenarioRegistry
        print("Available Scenarios:")
        for name in ScenarioRegistry.list():
            print(f"  - {name}")
        return
    
    if args.list_optimizers:
        from optimizers import OptimizerRegistry
        print("Available Optimizers:")
        for name in OptimizerRegistry.list():
            print(f"  - {name}")
        return
    
    if not args.scenario:
        parser.error("--scenario is required")
    
    try:
        run_pipeline(
            scenario_name=args.scenario,
            optimizer_name=args.optimizer,
            provider_name=args.provider,
            model_name=args.model,
            output_dir=args.output,
            evaluate_only=args.evaluate_only,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Part 10: Data Files

### 10.1 data/security_review.jsonl (20 test cases)

```jsonl
{"vars": {"code": "SELECT * FROM users WHERE name = '" + user_input + "'", "expected": "SQL injection vulnerability detected. Use parameterized queries."}}
{"vars": {"code": "const apiKey = 'sk-12345abcdef';", "expected": "Hardcoded API key detected. Use environment variables."}}
{"vars": {"code": "function checkAuth(req) { return true; }", "expected": "Missing authentication check. Implement proper auth verification."}}
{"vars": {"code": "crypto.createHash('md5').update(password).digest('hex')", "expected": "MD5 is cryptographically broken. Use SHA-256 or bcrypt."}}
{"vars": {"code": "fs.readFileSync(userFile, 'utf8');", "expected": "Path traversal risk. Validate and sanitize file paths."}}
{"vars": {"code": "eval(userInput);", "expected": "Dangerous eval() usage. Avoid dynamic code execution."}}
{"vars": {"code": "document.innerHTML = userContent;", "expected": "XSS vulnerability. Use textContent or sanitized HTML."}}
{"vars": {"code": "process.env.API_KEY in code", "expected": "Secret in environment. Use secrets management."}}
{"vars": {"code": "if (user.isAdmin) { grantAccess(); }", "expected": "Insecure direct reference. Verify admin status server-side."}}
{"vars": {"code": "jwt.sign({user: id}, null);", "expected": "JWT without expiration. Add exp claim."}}
{"vars": {"code": "os.system('rm -rf ' + user_input)", "expected": "Command injection risk. Never pass user input to system()."}}
{"vars": {"code": "new FileReader(userFile).readAsText(file)", "expected": "XXE vulnerability. Disable external entity parsing."}}
{"vars": {"code": "requests.get(user_url)", "expected": "SSRF vulnerability. Validate and whitelist URLs."}}
{"vars": {"code": "password.length > 6", "expected": "Weak password policy. Require stronger validation."}}
{"vars": {"code": "if (user.admin) { showAdminPanel(); }", "expected": "Insecure client-side check. Verify server-side."}}
{"vars": {"code": "sessionStorage.setItem('token', jwt)", "expected": "Token in localStorage. Use httpOnly cookies."}}
{"vars": {"code": "buffer.write(user_data)", "expected": "Buffer overflow risk. Validate input length."}}
{"vars": {"code": "String.format('SELECT * FROM %s', table_name)", "expected": "SQL injection via table name. Whitelist table names."}}
{"vars": {"code": "XMLParser.parse(user_xml)", "expected": "XXE injection. Use safe XML parser configuration."}}
{"vars": {"code": "Math.random() * 1000", "expected": "Insecure random. Use cryptographically secure RNG."}}
```

---

## Summary

| Aspect | Implementation |
|--------|---------------|
| **Architecture** | Sequential provider failover for rate limits |
| **Provider 1 (Primary)** | OpenCode CLI → GPT-4o-mini (OpenAI **FREE tier**) |
| **Provider 2 (Secondary)** | Qwen Code CLI → Qwen2.5-Coder:32b |
| **Provider 3 (Tertiary)** | Gemini CLI → Gemini 1.5 Flash |
| **Total Cost** | **$0** - All providers use free tier/self-hosted |
| **Scenarios** | Security review, Unit test, Documentation, API design |
| **Test cases** | 20 per scenario |
| **Optimizers** | MIPROv2, BootstrapFewShot, BootstrapFewShotWithRandomSearch |

---

*Generated: January 2026*
*Project: gemini-cli-prompt-library*
*Reference: dspy-helm (StanfordMIMI)*
*Strategy: Sequential Provider Failover for Rate Limit Rotation*
