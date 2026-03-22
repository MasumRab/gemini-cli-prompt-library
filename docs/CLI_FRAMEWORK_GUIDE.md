# CLI Framework Implementation Guide

**Project**: gemini-cli-prompt-library  
**Date**: 2026-01-18  
**Status**: Active Development

---

## Executive Summary

This guide documents CLI framework decisions for building agentic-compatible command-line tools. Based on session analysis (2026-01-13), the selected stack is **typer + rich + InquirerPy** with agentic wrappers.

---

## Stack Decision (TC-001)

```
typer + rich + InquirerPy
```

| Component | Role | Why |
|-----------|------|-----|
| **typer** | CLI command structure | Type hints → CLI args, Click underneath |
| **rich** | Terminal output | Tables, progress, syntax highlighting |
| **InquirerPy** | Interactive prompts | Fuzzy search, select menus, checkboxes |

---

## Part 1: CLI Command Frameworks

### 1.1 argparse (Current in dspy_helm/cli.py)

```python
# Current implementation
parser = argparse.ArgumentParser(
    description="DSPy-HELM: Evaluation and Optimization Framework",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
```

| Pros | Cons |
|------|------|
| Zero dependencies | Verbose, no type hints |
| Always available | Manual help formatting |
| Stable API | No auto-completion |
| ✅ Agentic safe | No rich integration |

**Best For**: Simple scripts, stdlib-only requirements

---

### 1.2 typer ✅ RECOMMENDED

| Pros | Cons |
|------|------|
| Type hints → CLI args | Extra dependency |
| Auto shell completion | Slightly slower startup |
| Rich integration built-in | |
| Click underneath (fallback) | |
| ✅ Agentic safe | |

**Migration Example**:
```python
# Before (argparse)
parser.add_argument("--scenario", type=str, required=True)
parser.add_argument("--optimizer", choices=["MIPROv2", "BootstrapFewShot"])

# After (typer)
from typing import Optional
from enum import Enum
import typer

class Optimizer(str, Enum):
    miprov2 = "MIPROv2"
    bootstrap = "BootstrapFewShot"

@app.command()
def run(
    scenario: str = typer.Argument(..., help="Scenario to run"),
    optimizer: Optional[Optimizer] = typer.Option(None, "-o", "--optimizer"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Run a DSPy-HELM evaluation."""
    ...
```

---

### 1.3 cyclopts (Typer Alternative)

| Pros | Cons |
|------|------|
| Fixes 13 Typer edge cases | Smaller community |
| Faster startup | Less documentation |
| Native JSON output | Newer project |
| Better boolean flags | |

**When to Choose**: Boolean flag handling critical, need native `--json`

---

### 1.4 python-fire

| Pros | Cons |
|------|------|
| Zero boilerplate | Ignores type hints |
| Any object → CLI | Magic behavior |
| ✅ Native headless | Debugging harder |

**Example**:
```python
import fire

class DSPyHELM:
    def evaluate(self, scenario: str, optimizer: str = None):
        return {"scenario": scenario, "optimizer": optimizer}

if __name__ == "__main__":
    fire.Fire(DSPyHELM)
```

**Best For**: Rapid prototyping, internal tools

---

## Part 2: Interactive Prompt Libraries

### 2.1 InquirerPy ⚠️ NEEDS WRAPPER

| Pros | Cons |
|------|------|
| Full Inquirer.js port | ❌ Blocks on no TTY |
| Fuzzy search | Requires wrapper |
| Async support | |
| Rich prompt types | |

**The Problem**:
```python
# This HANGS when run by AI agent (no TTY):
from InquirerPy import inquirer
result = inquirer.select(message="Choose:", choices=["A", "B"]).execute()
```

---

### 2.2 questionary

| Pros | Cons |
|------|------|
| Simpler API | ❌ Same TTY blocking |
| Good defaults | No async |
| | Fewer features |

---

### 2.3 prompt-toolkit

| Pros | Cons |
|------|------|
| Full readline | Complex API |
| Autocomplete | Overkill for simple prompts |
| Syntax highlighting | ⚠️ TTY issues |

**Best For**: REPLs, custom editors

---

## Part 3: Output Libraries

### 3.1 rich ✅ RECOMMENDED

| Pros | Cons |
|------|------|
| Tables, progress bars | Terminal detection edge cases |
| Syntax highlighting | |
| Markdown rendering | |
| ✅ Auto-detects non-TTY | |

**Usage**:
```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Results")
table.add_column("Metric")
table.add_column("Value")
table.add_row("Score", "0.95")
console.print(table)
```

---

### 3.2 Textual

| Pros | Cons |
|------|------|
| Full TUI framework | Heavier weight |
| CSS styling | Learning curve |
| Widgets, reactive | Overkill for simple CLI |
| ✅ Native headless mode | |

**Best For**: Full terminal applications, dashboards

---

## Part 4: Agentic Compatibility

### 4.1 Detection Module

```python
# src/utils/agentic.py
import os
import sys
from typing import TypeVar, List, Optional

T = TypeVar("T")

AGENT_INDICATORS = {
    "AGENT_MODE": "1",
    "CI": "true",
    "GITHUB_ACTIONS": "true",
    "NONINTERACTIVE": "1",
}

def is_agentic() -> bool:
    """Detect if running under an AI coding agent."""
    # TTY checks
    if not sys.stdin.isatty():
        return True
    if not sys.stdout.isatty():
        return True
    
    # Terminal type
    if os.environ.get("TERM") in ("dumb", ""):
        return True
    
    # Environment variables
    for var, expected in AGENT_INDICATORS.items():
        if os.environ.get(var) == expected:
            return True
    
    return False

def is_interactive() -> bool:
    return not is_agentic()
```

### 4.2 Smart Prompt Wrappers

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
    """Select with agentic fallback."""
    if is_agentic():
        return default if default else choices[0]
    
    from InquirerPy import inquirer
    return inquirer.select(
        message=message,
        choices=choices,
        default=default,
    ).execute()

def smart_confirm(message: str, default: bool = True) -> bool:
    """Confirm with agentic fallback."""
    if is_agentic():
        return default
    
    from InquirerPy import inquirer
    return inquirer.confirm(message=message, default=default).execute()

def smart_text(message: str, default: str = "") -> str:
    """Text input with agentic fallback."""
    if is_agentic():
        return default
    
    from InquirerPy import inquirer
    return inquirer.text(message=message, default=default).execute()

def smart_fuzzy(message: str, choices: List[str], default: str = None) -> str:
    """Fuzzy select with agentic fallback."""
    if is_agentic():
        return default or choices[0]
    
    from InquirerPy import inquirer
    return inquirer.fuzzy(message=message, choices=choices).execute()

def smart_checkbox(
    message: str,
    choices: List[str],
    defaults: List[str] = None,
) -> List[str]:
    """Checkbox with agentic fallback."""
    if is_agentic():
        return defaults or choices[:1]
    
    from InquirerPy import inquirer
    return inquirer.checkbox(message=message, choices=choices).execute()
```

### 4.3 Output Format Handler

```python
# src/utils/output.py
import json
import sys
from typing import Any, Optional
from enum import Enum
from rich.console import Console
from rich.table import Table

class OutputFormat(str, Enum):
    human = "human"
    json = "json"
    jsonl = "jsonl"

def get_console() -> Console:
    return Console(force_terminal=sys.stdout.isatty())

def output(data: Any, format: OutputFormat = OutputFormat.human, title: str = None):
    if format == OutputFormat.json:
        print(json.dumps(data, indent=2, default=str))
    elif format == OutputFormat.jsonl:
        if isinstance(data, list):
            for item in data:
                print(json.dumps(item, default=str))
        else:
            print(json.dumps(data, default=str))
    else:
        console = get_console()
        if isinstance(data, list) and data and isinstance(data[0], dict):
            table = Table(title=title)
            for key in data[0].keys():
                table.add_column(str(key))
            for row in data:
                table.add_row(*[str(v) for v in row.values()])
            console.print(table)
        else:
            console.print(data)
```

---

## Part 5: Comparison Matrix

### CLI Frameworks

| Feature | argparse | typer | cyclopts | fire | click |
|---------|----------|-------|----------|------|-------|
| Type Hints → Args | ❌ | ✅ | ✅ | ❌ | ❌ |
| Auto Completion | ❌ | ✅ | ✅ | ❌ | ✅ |
| Rich Integration | ❌ | ✅ | ⚠️ | ❌ | ⚠️ |
| Zero Dependencies | ✅ | ❌ | ❌ | ❌ | ❌ |
| Agentic Safe | ✅ | ✅ | ✅ | ✅ | ✅ |

### Interactive Libraries

| Feature | InquirerPy | questionary | prompt-toolkit |
|---------|------------|-------------|----------------|
| Fuzzy Search | ✅ | ❌ | ⚠️ |
| Async | ✅ | ❌ | ✅ |
| Agentic Safe | ⚠️ Wrapper | ⚠️ Wrapper | ⚠️ Wrapper |

### Output Libraries

| Feature | rich | Textual |
|---------|------|---------|
| Tables | ✅ | ✅ |
| Progress | ✅ | ✅ |
| Headless | ✅ Auto | ✅ Native |
| Weight | Medium | Heavy |

---

## Part 6: Migration Plan

### Phase 1: Add Dependencies
```bash
pip install typer rich InquirerPy
```

### Phase 2: Create Utils
```
src/
├── utils/
│   ├── __init__.py
│   ├── agentic.py      # is_agentic()
│   ├── prompts.py      # smart_* wrappers
│   └── output.py       # format handlers
```

### Phase 3: Migrate dspy_helm/cli.py
- Keep argparse as fallback
- Add typer commands alongside
- Gradually migrate commands

### Phase 4: Add Interactive Workflows
- Use smart_* wrappers
- Test in both human and agentic modes

---

## Testing

### CLI Testing
```python
from typer.testing import CliRunner
runner = CliRunner()

def test_json_output():
    result = runner.invoke(app, ["evaluate", "test", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)
```

### Agentic Mode Testing
```python
def test_is_agentic(monkeypatch):
    monkeypatch.setenv("AGENT_MODE", "1")
    assert is_agentic() == True
```

---

---

## Part 7: Rich Library Deep Dive

### Features Available

| Feature | Description | Code Example |
|---------|-------------|--------------|
| **Console** | Central output control | `Console(force_terminal=False)` |
| **Tables** | Formatted data display | `Table(title="Results")` |
| **Progress** | Progress bars, spinners | `track(items)` |
| **Syntax** | Code highlighting | `Syntax(code, "python")` |
| **Markdown** | Render markdown | `Markdown("# Title")` |
| **Panels** | Bordered boxes | `Panel("content", title="Info")` |
| **Trees** | Hierarchical data | `Tree("root")` |
| **Pretty** | Object inspection | `Pretty(data)` |

### Agentic-Safe Patterns

```python
from rich.console import Console
import sys

# Auto-detect TTY
console = Console()  # force_terminal auto-detected

# Explicit control
console = Console(
    force_terminal=sys.stdout.isatty(),
    force_interactive=sys.stdin.isatty(),
    no_color=os.environ.get("NO_COLOR") is not None,
)

# JSON fallback pattern
def output_result(data: dict, json_mode: bool = False):
    if json_mode:
        import json
        print(json.dumps(data, indent=2))
    else:
        console.print(data)
```

---

## Part 8: Textual Deep Dive

### When to Use Textual vs Rich

| Use Case | Library |
|----------|---------|
| Simple CLI output | rich |
| Tables, progress bars | rich |
| Full interactive TUI | Textual |
| Dashboard application | Textual |
| Form-based workflows | Textual |
| File browser | Textual |

### Headless Mode for Testing

```python
from textual.pilot import Pilot

async def test_app():
    """Run Textual app in headless mode."""
    async with MyApp().run_test() as pilot:
        # Simulate user interactions
        await pilot.press("tab")
        await pilot.press("enter")
        await pilot.click("#submit")
        
        # Assert on UI state
        assert pilot.app.query_one("#result").text == "Success"
```

### Textual for Future Features

Consider Textual for:
- Prompt optimization dashboard
- Real-time evaluation monitoring
- Interactive scenario builder
- DSPy module explorer

---

## Part 9: InquirerPy Prompt Types Reference

| Type | Import | Use Case | Agentic Fallback |
|------|--------|----------|------------------|
| `select` | `inquirer.select()` | Single choice | First/default |
| `checkbox` | `inquirer.checkbox()` | Multiple choices | Defaults list |
| `text` | `inquirer.text()` | Free text | Default string |
| `confirm` | `inquirer.confirm()` | Yes/No | Default bool |
| `fuzzy` | `inquirer.fuzzy()` | Searchable list | First/default |
| `filepath` | `inquirer.filepath()` | File picker | Default path |
| `secret` | `inquirer.secret()` | Password | Empty string |
| `number` | `inquirer.number()` | Numeric | Default number |
| `rawlist` | `inquirer.rawlist()` | Numbered list | First |
| `expand` | `inquirer.expand()` | Shortcut keys | Default key |

### Complete Wrapper Implementation

```python
# src/utils/prompts.py
from typing import List, TypeVar, Optional, Union
from pathlib import Path
from .agentic import is_agentic

T = TypeVar("T")

def smart_select(
    message: str,
    choices: List[T],
    default: Optional[T] = None,
) -> T:
    if is_agentic():
        return default if default is not None else choices[0]
    from InquirerPy import inquirer
    return inquirer.select(message=message, choices=choices, default=default).execute()

def smart_checkbox(
    message: str,
    choices: List[str],
    defaults: Optional[List[str]] = None,
) -> List[str]:
    if is_agentic():
        return defaults if defaults else []
    from InquirerPy import inquirer
    return inquirer.checkbox(message=message, choices=choices).execute()

def smart_text(message: str, default: str = "") -> str:
    if is_agentic():
        return default
    from InquirerPy import inquirer
    return inquirer.text(message=message, default=default).execute()

def smart_confirm(message: str, default: bool = True) -> bool:
    if is_agentic():
        return default
    from InquirerPy import inquirer
    return inquirer.confirm(message=message, default=default).execute()

def smart_fuzzy(
    message: str,
    choices: List[str],
    default: Optional[str] = None,
) -> str:
    if is_agentic():
        return default if default else choices[0]
    from InquirerPy import inquirer
    return inquirer.fuzzy(message=message, choices=choices).execute()

def smart_filepath(
    message: str,
    default: Union[str, Path] = "",
    only_directories: bool = False,
) -> str:
    if is_agentic():
        return str(default)
    from InquirerPy import inquirer
    return inquirer.filepath(
        message=message,
        default=str(default),
        only_directories=only_directories,
    ).execute()

def smart_number(
    message: str,
    default: Optional[float] = None,
    min_allowed: Optional[float] = None,
    max_allowed: Optional[float] = None,
) -> float:
    if is_agentic():
        return default if default is not None else 0
    from InquirerPy import inquirer
    return inquirer.number(
        message=message,
        default=default,
        min_allowed=min_allowed,
        max_allowed=max_allowed,
    ).execute()

def smart_secret(message: str, default: str = "") -> str:
    """Password input. Returns default in agentic mode."""
    if is_agentic():
        return default  # Or check env var
    from InquirerPy import inquirer
    return inquirer.secret(message=message).execute()
```

---

## Related Documentation

- [CLI_LIBRARY_MATRIX.md](./CLI_LIBRARY_MATRIX.md) - Complete comparison matrices
- [AGENTIC_COMPATIBILITY.md](./AGENTIC_COMPATIBILITY.md) - Agentic detection and wrappers
- [SESSION_ANALYSIS.md](./SESSION_ANALYSIS.md) - Session history and decisions

---

## References

- **Session**: 2026-01-13T10-46 (CLI framework decision)
- **Technical Constraint**: TC-001 (typer + rich + InquirerPy)
- [Typer Docs](https://typer.tiangolo.com/)
- [Cyclopts Docs](https://cyclopts.readthedocs.io/)
- [Rich Docs](https://rich.readthedocs.io/)
- [Textual Docs](https://textual.textualize.io/)
- [InquirerPy Docs](https://inquirerpy.readthedocs.io/)
- [Python Fire Docs](https://github.com/google/python-fire)
