# Agentic Compatibility Guide

**Project**: gemini-cli-prompt-library  
**Purpose**: Ensure CLI tools work with AI coding agents

---

## Overview

AI coding agents (Claude Code, Amp, OpenCode, Gemini CLI, etc.) run commands without a TTY. Interactive prompts that require user input will **hang indefinitely** unless properly wrapped.

---

## The Problem

```python
# ❌ This HANGS when run by an AI agent:
from InquirerPy import inquirer
result = inquirer.select(message="Choose:", choices=["A", "B"]).execute()
```

When an AI agent runs this code:
1. No TTY is attached (`sys.stdin.isatty() == False`)
2. InquirerPy waits for keyboard input
3. Command hangs forever
4. Agent times out or kills the process

---

## The Solution

### 1. Detect Agentic Environment

```python
# src/utils/agentic.py
import os
import sys

def is_agentic() -> bool:
    """Detect if running under an AI coding agent or CI."""
    
    # TTY checks (most reliable)
    if not sys.stdin.isatty():
        return True
    if not sys.stdout.isatty():
        return True
    
    # Terminal type
    if os.environ.get("TERM") in ("dumb", ""):
        return True
    
    # Known agent/CI environment variables
    agent_vars = {
        "AGENT_MODE": "1",
        "CI": "true",
        "GITHUB_ACTIONS": "true",
        "GITLAB_CI": "true",
        "NONINTERACTIVE": "1",
    }
    
    for var, expected in agent_vars.items():
        if os.environ.get(var) == expected:
            return True
    
    return False

def is_interactive() -> bool:
    """Inverse of is_agentic()."""
    return not is_agentic()
```

### 2. Wrap Interactive Prompts

```python
# src/utils/prompts.py
from typing import List, TypeVar, Optional
from .agentic import is_agentic

T = TypeVar("T")

def smart_select(
    message: str,
    choices: List[T],
    default: Optional[T] = None,
) -> T:
    """Select from choices. Uses default in agentic mode."""
    if is_agentic():
        if default is not None:
            return default
        return choices[0]  # First choice as fallback
    
    from InquirerPy import inquirer
    return inquirer.select(
        message=message,
        choices=choices,
        default=default,
    ).execute()

def smart_confirm(message: str, default: bool = True) -> bool:
    """Confirm prompt. Uses default in agentic mode."""
    if is_agentic():
        return default
    
    from InquirerPy import inquirer
    return inquirer.confirm(message=message, default=default).execute()

def smart_text(message: str, default: str = "") -> str:
    """Text input. Uses default in agentic mode."""
    if is_agentic():
        return default
    
    from InquirerPy import inquirer
    return inquirer.text(message=message, default=default).execute()

def smart_password(message: str) -> str:
    """Password input. Returns empty in agentic mode."""
    if is_agentic():
        return ""  # Or raise an error
    
    from InquirerPy import inquirer
    return inquirer.secret(message=message).execute()

def smart_fuzzy(
    message: str,
    choices: List[str],
    default: Optional[str] = None,
) -> str:
    """Fuzzy search select. Uses default in agentic mode."""
    if is_agentic():
        return default or choices[0]
    
    from InquirerPy import inquirer
    return inquirer.fuzzy(
        message=message,
        choices=choices,
        default=default,
    ).execute()

def smart_checkbox(
    message: str,
    choices: List[str],
    defaults: Optional[List[str]] = None,
) -> List[str]:
    """Multi-select. Uses defaults in agentic mode."""
    if is_agentic():
        return defaults or []
    
    from InquirerPy import inquirer
    return inquirer.checkbox(
        message=message,
        choices=choices,
        default=defaults,
    ).execute()

def smart_filepath(
    message: str,
    default: str = "",
    only_directories: bool = False,
) -> str:
    """File path input. Uses default in agentic mode."""
    if is_agentic():
        return default
    
    from InquirerPy import inquirer
    return inquirer.filepath(
        message=message,
        default=default,
        only_directories=only_directories,
    ).execute()
```

### 3. Support JSON Output

```python
# src/utils/output.py
import json
import sys
from typing import Any
from enum import Enum
from rich.console import Console

class OutputFormat(str, Enum):
    human = "human"
    json = "json"

def get_console() -> Console:
    """Get console configured for environment."""
    return Console(force_terminal=sys.stdout.isatty())

def output(data: Any, format: OutputFormat = OutputFormat.human):
    """Output data in specified format."""
    if format == OutputFormat.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        get_console().print(data)
```

---

## Library Compatibility Matrix

### ✅ Agentic Safe (No Changes Needed)

| Library | Notes |
|---------|-------|
| **typer** | CLI args, `--json` flag pattern |
| **cyclopts** | Native JSON mode |
| **python-fire** | Native headless |
| **rich** | Auto-detects non-TTY via `force_terminal` |
| **Textual** | Native headless mode for testing |
| **argparse** | Pure text I/O |

### ⚠️ Needs Wrapper

| Library | Problem | Solution |
|---------|---------|----------|
| **InquirerPy** | Blocks on no TTY | Use `smart_*` wrappers |
| **questionary** | Blocks on no TTY | Use `smart_*` wrappers |
| **prompt-toolkit** | May block | Careful handling |

---

## Usage Patterns

### Pattern 1: CLI with --json Flag

```python
import typer
from enum import Enum

app = typer.Typer()

class Format(str, Enum):
    human = "human"
    json = "json"

@app.command()
def list_scenarios(
    format: Format = typer.Option(Format.human, "--format", "-f"),
):
    """List available scenarios."""
    scenarios = ["security_review", "unit_test", "documentation"]
    
    if format == Format.json:
        import json
        print(json.dumps(scenarios))
    else:
        for s in scenarios:
            print(f"  - {s}")
```

### Pattern 2: Interactive Workflow with Fallback

```python
from src.utils.prompts import smart_select, smart_confirm
from src.utils.agentic import is_agentic

def guided_workflow():
    """Run guided workflow with agentic fallback."""
    
    # Select scenario
    scenario = smart_select(
        message="Select scenario:",
        choices=["security_review", "unit_test", "documentation"],
        default="security_review",  # Used in agentic mode
    )
    
    # Confirm optimization
    optimize = smart_confirm(
        message="Run optimization?",
        default=True,  # Used in agentic mode
    )
    
    # In agentic mode, print what was selected
    if is_agentic():
        print(f"[agentic] Selected: {scenario}, optimize={optimize}")
    
    return run_scenario(scenario, optimize)
```

### Pattern 3: Explicit Agentic Override

```python
@app.command()
def evaluate(
    scenario: str = typer.Argument(...),
    agentic: bool = typer.Option(False, "--agentic", hidden=True),
):
    """Evaluate a scenario."""
    import os
    
    # Allow explicit override
    if agentic:
        os.environ["AGENT_MODE"] = "1"
    
    # Now is_agentic() will return True
    ...
```

---

## Testing

### Test Agentic Detection

```python
import pytest
from src.utils.agentic import is_agentic

def test_agentic_with_env(monkeypatch):
    monkeypatch.setenv("AGENT_MODE", "1")
    assert is_agentic() == True

def test_agentic_ci(monkeypatch):
    monkeypatch.setenv("CI", "true")
    assert is_agentic() == True

def test_interactive_default(monkeypatch):
    # Clear all agentic indicators
    for var in ["AGENT_MODE", "CI", "GITHUB_ACTIONS"]:
        monkeypatch.delenv(var, raising=False)
    # Note: isatty() still affects result in real terminal
```

### Test Smart Prompts in Agentic Mode

```python
def test_smart_select_agentic(monkeypatch):
    monkeypatch.setenv("AGENT_MODE", "1")
    
    from src.utils.prompts import smart_select
    result = smart_select(
        message="Choose:",
        choices=["A", "B", "C"],
        default="B",
    )
    assert result == "B"  # Uses default

def test_smart_confirm_agentic(monkeypatch):
    monkeypatch.setenv("AGENT_MODE", "1")
    
    from src.utils.prompts import smart_confirm
    assert smart_confirm("Proceed?", default=True) == True
    assert smart_confirm("Proceed?", default=False) == False
```

### Test JSON Output

```python
from typer.testing import CliRunner
from myapp import app

runner = CliRunner()

def test_json_output():
    result = runner.invoke(app, ["list", "--format", "json"])
    assert result.exit_code == 0
    
    import json
    data = json.loads(result.stdout)
    assert isinstance(data, list)
```

---

## Environment Variables

| Variable | Value | Effect |
|----------|-------|--------|
| `AGENT_MODE` | `1` | Force agentic mode |
| `CI` | `true` | Detected as agentic |
| `GITHUB_ACTIONS` | `true` | Detected as agentic |
| `NONINTERACTIVE` | `1` | Force non-interactive |
| `TERM` | `dumb` | No terminal capabilities |
| `NO_COLOR` | any | Disable colors (rich respects this) |

---

## Best Practices

1. **Always provide defaults** for interactive prompts
2. **Support --json flag** on all commands
3. **Log selected values** in agentic mode for debugging
4. **Test both modes** in CI
5. **Document agentic behavior** for each command
6. **Never block** on user input without fallback

---

## Common Pitfalls

### ❌ Don't Do This
```python
# No default - will select first item in agentic mode
result = smart_select("Choose:", ["dangerous", "safe"])
```

### ✅ Do This Instead
```python
# Explicit safe default
result = smart_select("Choose:", ["dangerous", "safe"], default="safe")
```

### ❌ Don't Do This
```python
# Required password with no fallback
password = smart_password("Enter API key:")
# In agentic mode, returns empty string - breaks auth
```

### ✅ Do This Instead
```python
# Check environment first
password = os.environ.get("API_KEY") or smart_password("Enter API key:")
```
