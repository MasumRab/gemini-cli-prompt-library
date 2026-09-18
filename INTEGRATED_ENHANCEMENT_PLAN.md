# Integrated Enhancement Plan v3

**Version**: 3.0  
**Date**: January 18, 2026  
**Purpose**: Integrate Enhancement Plan and CASS patterns into our roadmap

---

## Part 1: Current State Analysis

### 1.1 What We Have

| Component | Status | Notes |
|-----------|--------|-------|
| **CLI** | ✅ Complete | 8 commands (improve, evaluate, convert, list, optimize, compare, interactive, sessions) |
| **TOML Manager** | ✅ Complete | 41 prompt files, variable extraction, scoring |
| **Improve Module** | ✅ Complete | ImproveSignature, ImproveModule with ChainOfThought |
| **Module Registry** | ✅ Complete | 7 scenarios registered (code_review, architecture, etc.) |
| **Framework** | ❌ Missing | dspy_helm not consolidated |
| **Interactive Mode** | ⚠️ Placeholder | Prints "Phase 3 feature" |
| **5 Approaches** | ⚠️ Partial | TOML + DSPy only, others pending |

### 1.2 Command Categories (41 TOML files)

```
architecture/     → 4 files (design patterns, system design, API, database)
code-review/      → 4 files (best practices, performance, refactor, security)
debugging/        → 1 file (trace-issue)
docs/             → 2 files (write-readme, api-docs)
learning/         → 4 files (explain-concept, compare-tech, roadmap, eli5)
prompts/          → 9 files (refine, best-practices, dspy-convert, evaluate, etc.)
testing/          → 3 files (edge-cases, generate-e2e, generate-unit)
workflows/        → 4 files (feature-dev, comprehensive-test, smart-refactor, prompt-refinery)
writing/          → 2 files (write-blog, write-email)
debugging/        → 1 file (trace-issue)
learning/         → 4 files
```

---

## Part 2: Enhancement Plan Integration

### 2.1 Comparison: Our Plan vs Enhancement Plan

| Aspect | Our Plan | Enhancement Plan | Gap |
|--------|----------|------------------|-----|
| **Entry Point** | `/prompts:improve` | `/prompts:improve` | Same |
| **Command Selection** | User manually picks | Intelligent Dispatcher | Need dispatcher |
| **UI Feedback** | Text output | Command Recommendation Menu | Need rich UI |
| **Alternatives** | `compare` command | cass-augmented suggestions | Need cass integration |
| **Workflow Tracking** | `sessions` placeholder | Progression Checklist | Need async tracking |
| **Agent Integration** | Future Phase 4 | Proactive suggestions | Need agent skills |

### 2.2 Required Additions for Enhancement Plan

| Feature | Priority | Where |
|---------|----------|-------|
| **Command Manifest** | HIGH | `framework/manifest.toml` or `framework/registry.py` |
| **Intelligent Dispatcher** | HIGH | New meta-prompt + dispatch logic |
| **Rich UI/Menu System** | MEDIUM | `cli.py` enhancement or new `ui.py` |
| **CASS Integration** | MEDIUM | New module for historical search |
| **Async Task Tracking** | LOW | `framework/tasks.py` for workflows |
| **Progression Checklist** | LOW | TUI enhancement |

---

## Part 3: CASS Pattern Integration

### 3.1 CASS Patterns We Can Adopt

| Pattern | Description | Our Implementation |
|---------|-------------|-------------------|
| **Edge N-Gram Indexing** | Pre-compute prefix matches for O(1) lookup | Add to `toml.py` search |
| **Hash Embedder** | FNV-1a fallback for semantic search | Add `hash_embedder.py` |
| **Memory-Mapped Index** | CVVI binary format for vectors | Add `vector_index.py` |
| **Forgiving CLI Parsing** | Typo correction, flag normalization | Add to `cli.py` |
| **Robot Mode** | Structured JSON for AI agents | Add `--robot` flag |
| **PathTrie** | O(k) workspace path rewriting | Add for remote sources |
| **Connectors** | Trait-based agent format readers | Pattern for new connectors |

### 3.2 Priority CASS Features to Add

| Priority | Feature | File | Benefit |
|----------|---------|------|---------|
| HIGH | Forgiving CLI parsing | `cli.py` | Better AI agent compatibility |
| HIGH | Robot/JSON mode | `cli.py` | Structured output for automation |
| MEDIUM | Hash embedder | `modules/embeddings.py` | Zero-dep semantic search |
| MEDIUM | Edge n-gram | `toml.py` | Faster prefix search |

---

## Part 4: Integrated Roadmap v3

### Phase 1: Foundation (COMPLETE) ✅
- [x] CLI with 8 commands
- [x] TOML manager with scoring
- [x] ImproveModule with ChainOfThought
- [x] Module registry

### Phase 2: Framework Consolidation + Dispatcher (NEXT)
| Task | Subtask | Status |
|------|---------|--------|
| 2.1 Create `framework/` | `framework/__init__.py` | PENDING |
| 2.2 Create Command Manifest | `framework/registry.py` | **NEW** |
| 2.3 Create Intelligent Dispatcher | `framework/dispatcher.py` | **NEW** |
| 2.4 Consolidate dspy_helm | Move providers, optimizers, etc. | PENDING |
| 2.5 Add Forgiving CLI | Typo correction, flag normalization | **NEW** |
| 2.6 Add Robot Mode | `--robot`, `--json` output | **NEW** |
| 2.7 Fix CLI bugs | Complete unimplemented methods | PENDING |

### Phase 3: UI + CASS Integration
| Task | Subtask | Status |
|------|---------|--------|
| 3.1 Command Menu UI | Rich recommendation display | **NEW** |
| 3.2 cass-augmented Suggestions | Historical search integration | **NEW** |
| 3.3 Implement Interactive Mode | Full REPL with state | PENDING |
| 3.4 Implement All 5 Approaches | MIPROv2, Bootstrap, Custom | PENDING |
| 3.5 Add Hash Embedder | FNV-1a semantic fallback | **NEW** |
| 3.6 Add Edge N-Gram | Fast prefix search | **NEW** |

### Phase 4: Agentic Integration
| Task | Subtask | Status |
|------|---------|--------|
| 4.1 Proactive Suggestions | Agent recommends workflows | **NEW** |
| 4.2 Self-Correction Skills | Internal dispatcher for errors | **NEW** |
| 4.3 Async Task Tracking | Workflow progress | **NEW** |
| 4.4 Progression Checklist | TUI for long-running tasks | **NEW** |

### Phase 5: Cleanup
| Task | Status |
|------|--------|
| Delete `dspy_helm/` (after consolidation) | PENDING |
| Delete `dspy_integration/optimizers/` | PENDING |
| Run full test suite | PENDING |

---

## Part 5: Detailed Implementation Tasks

### 5.1 Phase 2 Tasks

#### Task 2.1: Create framework/__init__.py
```python
# framework/__init__.py
"""Framework exports for dspy_integration."""

from .registry import CommandRegistry, get_command
from .dispatcher import IntelligentDispatcher
from .providers import get_provider
from .optimizers import get_optimizer

__all__ = [
    "CommandRegistry",
    "get_command",
    "IntelligentDispatcher",
    "get_provider",
    "get_optimizer",
]
```

#### Task 2.2: Create Command Registry (NEW - Critical)
```python
# framework/registry.py
"""Command manifest and registry.

Automatically discovers all commands from commands/ directory.
Provides metadata for Intelligent Dispatcher.
"""

from pathlib import Path
from typing import Dict, List, Optional
import tomllib

class CommandRegistry:
    """Registry of all available commands."""
    
    def __init__(self, root: Path = Path("commands")):
        self.root = Path(root)
        self._commands: Dict[str, Dict] = {}
        self._load_all()
    
    def _load_all(self):
        """Load metadata from all TOML files."""
        for toml_file in self.root.rglob("*.toml"):
            metadata = self._load_metadata(toml_file)
            self._commands[metadata["name"]] = metadata
    
    def _load_metadata(self, path: Path) -> Dict:
        """Load command metadata from TOML."""
        content = path.read_text()
        data = tomllib.loads(content)
        return {
            "name": path.stem,
            "category": path.parent.name,
            "path": str(path),
            "description": data.get("description", ""),
            "args": data.get("args", ""),
            "examples": data.get("examples", []),
        }
    
    def get_command(self, name: str) -> Optional[Dict]:
        """Get command metadata by name."""
        return self._commands.get(name)
    
    def list_by_category(self, category: str) -> List[str]:
        """List commands in a category."""
        return [n for n, m.items() if m in self._commands["category"] == category]
    
    def search(self, query: str) -> List[Dict]:
        """Search commands by keyword."""
        results = []
        for name, meta in self._commands.items():
            if query.lower() in meta["description"].lower():
                results.append(meta)
        return results
```

#### Task 2.3: Create Intelligent Dispatcher (NEW - Critical)
```python
# framework/dispatcher.py
"""Intelligent Dispatcher for natural language to command routing.

Uses a meta-prompt to analyze user requests and select the best command.
"""

from typing import Dict, List, Optional, Tuple
from .registry import CommandRegistry

class IntelligentDispatcher:
    """Routes natural language requests to appropriate commands."""
    
    def __init__(self, registry: CommandRegistry):
        self.registry = registry
    
    def dispatch(self, user_request: str) -> Dict:
        """
        Analyze user request and return best command match.
        
        Returns:
            {
                "command": str,           # e.g., "/code-review:security"
                "refined_prompt": str,    # Optimized prompt for command
                "confidence": float,       # 0.0 to 1.0
                "alternatives": List[Dict],  # Other possible commands
                "reasoning": str          # Why this command was chosen
            }
        """
        # Step 1: Get all available commands
        all_commands = list(self.registry._commands.values())
        
        # Step 2: Use LLM or heuristic to select best command
        # For MVP, use keyword matching
        best_match = self._keyword_match(user_request, all_commands)
        
        # Step 3: Generate refined prompt
        refined_prompt = self._refine_prompt(user_request, best_match)
        
        # Step 4: Find alternatives
        alternatives = self._find_alternatives(user_request, best_match, all_commands)
        
        return {
            "command": best_match["name"],
            "refined_prompt": refined_prompt,
            "confidence": best_match.get("confidence", 0.8),
            "alternatives": alternatives,
            "reasoning": best_match.get("reasoning", "Matched by keyword analysis"),
        }
    
    def _keyword_match(self, request: str, commands: List[Dict]) -> Dict:
        """Simple keyword matching for MVP."""
        request_lower = request.lower()
        keywords = request_lower.split()
        
        best_score = 0
        best_cmd = commands[0]
        
        for cmd in commands:
            score = sum(1 for kw in keywords if kw in cmd["description"].lower())
            if score > best_score:
                best_score = score
                best_cmd = cmd
        
        best_cmd["confidence"] = best_score / max(len(keywords), 1)
        best_cmd["reasoning"] = f"Matched {best_score} keywords"
        return best_cmd
    
    def _refine_prompt(self, request: str, command: Dict) -> str:
        """Generate optimized prompt for the selected command."""
        # Load the command's TOML and inject user's request
        # This is a placeholder - full implementation uses LLM
        return request
    
    def _find_alternatives(self, request: str, best: Dict, commands: List[Dict]) -> List[Dict]:
        """Find alternative commands that might also apply."""
        # Return top 3 alternatives by keyword overlap
        return []
```

#### Task 2.4: Add Forgiving CLI Parsing (NEW)
```python
# In cli.py - Add to main()
def normalize_args(args: List[str]) -> List[str]:
    """Normalize arguments for AI agent compatibility."""
    normalized = []
    i = 0
    while i < len(args):
        arg = args[i]
        
        # Single-dash to double-dash
        if arg.startswith("-") and not arg.startswith("--") and len(arg) > 2:
            normalized.append(f"--{arg[1:]}")
        # Flag typo correction (edit distance <= 2)
        elif arg.startswith("--"):
            normalized.append(_correct_flag_typo(arg))
        else:
            normalized.append(arg)
        i += 1
    
    return normalized
```

#### Task 2.5: Add Robot Mode (NEW)
```python
# In cli.py - Add to argument parser
robot_parser = subparsers.add_parser("robot", help="Robot/AI mode output")
robot_parser.add_argument("--robot", action="store_true", help="Enable robot mode")
robot_parser.add_argument("--robot-format", choices=["json", "jsonl", "compact"], default="json")
robot_parser.add_argument("--robot-meta", action="store_true", help="Include performance metadata")
robot_parser.add_argument("--fields", help="Comma-separated fields to include")
robot_parser.add_argument("--max-content-length", type=int, help="Truncate long fields")
robot_parser.add_argument("--max-tokens", type=int, help="Soft token budget")
```

---

## Part 6: File Changes Summary

### Files to CREATE (Phase 2)

| File | Lines | Purpose |
|------|-------|---------|
| `dspy_integration/framework/__init__.py` | 30 | Framework exports |
| `dspy_integration/framework/registry.py` | 150 | Command manifest |
| `dspy_integration/framework/dispatcher.py` | 120 | Intelligent dispatcher |
| `dspy_integration/framework/providers/__init__.py` | 50 | Provider exports |
| `dspy_integration/framework/optimizers/__init__.py` | 50 | Optimizer exports |
| `dspy_integration/framework/evaluation/__init__.py` | 50 | Evaluation exports |
| `dspy_integration/framework/scenarios/__init__.py` | 50 | Scenario exports |
| `dspy_integration/framework/data/__init__.py` | 30 | Data exports |
| `dspy_integration/framework/config/__init__.py` | 30 | Config exports |
| `dspy_integration/framework/prompts/__init__.py` | 50 | Prompt exports |

### Files to MODIFY (Phase 2)

| File | Changes |
|------|---------|
| `dspy_integration/cli.py` | Add forgiving parsing, robot mode, dispatcher integration |
| `dspy_integration/__init__.py` | Add framework exports |

### Files to DELETE (Phase 5)

| File | Reason |
|------|--------|
| `dspy_integration/optimizers/` | Replaced by `framework/optimizers/` |
| `dspy_helm/` | Consolidated into `framework/` |

---

## Part 7: Backward Compatibility

### 7.1 Ensuring Compatibility

| Old Interface | New Interface | Status |
|---------------|---------------|--------|
| `python -m dspy_integration improve "x"` | Same | ✅ Works |
| `python -m dspy_integration list` | Same | ✅ Works |
| `get_module_for_scenario("improve")` | Same | ✅ Works |
| `commands/prompts/improve.toml` | Same | ✅ Works |

### 7.2 New Interfaces

| New Interface | Phase |
|---------------|-------|
| `dispatcher.dispatch("fix my login bug")` | Phase 2 |
| `registry.list_by_category("workflows")` | Phase 2 |
| `cli --robot --json` | Phase 2 |
| `cass search "login error"` | Phase 3 (integration) |

---

## Part 8: Testing Strategy

### 8.1 Unit Tests

```python
# tests/test_registry.py
def test_load_all_commands():
    registry = CommandRegistry()
    assert len(registry._commands) == 41  # All TOML files

def test_search_by_keyword():
    registry = CommandRegistry()
    results = registry.search("security")
    assert len(results) > 0

# tests/test_dispatcher.py
def test_dispatch_returns_structure():
    dispatcher = IntelligentDispatcher(CommandRegistry())
    result = dispatcher.dispatch("check my code for vulnerabilities")
    assert "command" in result
    assert "refined_prompt" in result
    assert "confidence" in result
```

### 8.2 Integration Tests

```python
# tests/test_cli_robot.py
def test_robot_mode_json():
    result = run_cli(["--robot", "--json", "list"])
    assert result.is_json
    assert "scenarios" in result.data

def test_forgiving_parsing():
    # Single-dash long flag should work
    result = run_cli(["-robot", "-output", "json", "list"])
    assert result.success
```

---

## Summary: What's Changed from v2

| Change | Description |
|--------|-------------|
| **Added Command Registry** | New `framework/registry.py` for command discovery |
| **Added Intelligent Dispatcher** | New `framework/dispatcher.py` for NL routing |
| **Added Forgiving CLI** | Typo correction, flag normalization |
| **Added Robot Mode** | Structured JSON output for AI agents |
| **Added CASS Patterns** | Edge n-gram, hash embedder in future phases |
| **Removed Phase 3/4 tasks** | Absorbed into integrated roadmap |

---

## Next Steps

1. **Start Phase 2** - Create `framework/` directory structure
2. **Implement Registry** - Auto-discover 41 commands
3. **Implement Dispatcher** - Basic keyword matching
4. **Add Forgiving CLI** - Better AI compatibility
5. **Add Robot Mode** - Structured output

---

*Document Version: 3.0*  
*Last Updated: January 18, 2026*  
*Status: Ready for Phase 2 implementation*
