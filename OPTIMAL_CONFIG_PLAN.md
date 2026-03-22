# Optimal Configuration Implementation Plan

**Version**: 2.0  
**Date**: January 18, 2026  
**Updated**: January 18, 2026 (v2 - Post Phase 1 implementation)  
**Mode**: Implementation Mode (Phase 1 Complete)

---

## Executive Summary

This plan implements the **Optimal Configuration** for gemini-cli-prompt-library with full DSPy-HELM consolidation, unified CLI, and interactive tuning capabilities.

**Current Status:** Phase 1 (Foundation) COMPLETE  
**Next:** Phase 2 (Framework Consolidation)

---

## Part 1: Current Directory Structure

### 1.1 Actual Structure (After Phase 1)

```
gemini-cli-prompt-library/
├── commands/                          # EXISTING - TOML prompts (40+ files)
├── dspy_integration/                  # UNIFIED - All DSPy functionality
│   ├── __init__.py                    # UPDATED - Exports get_module_for_scenario
│   ├── __main__.py                    # NEW - Entry point for python -m dspy_integration
│   ├── cli.py                         # NEW - Unified CLI (11KB)
│   ├── toml.py                        # NEW - TOML wrapper with scoring (6KB)
│   ├── optimizers/                    # EXISTING - TO BE DELETED (replaced by framework/)
│   │   ├── __init__.py
│   │   └── optimize_module.py
│   ├── modules/                       # EXISTING - Core modules
│   │   ├── __init__.py                # UPDATED - Registered "improve" scenario
│   │   ├── architecture.py
│   │   ├── code_review.py
│   │   ├── documentation.py           # FIXED - self.generate → self.program
│   │   ├── feature_dev.py
│   │   ├── improve.py                 # NEW - ImproveModule (4KB)
│   │   ├── security_review.py
│   │   └── unit_test.py               # FIXED - self.generate → self.program
│   ├── PHASE1_TODOS.md                # NEW - Phase tracking
│   ├── PHASE2_TODOS.md                # NEW - Phase tracking
│   ├── PHASE3_TODOS.md                # NEW - Phase tracking
│   └── PHASE4_TODOS.md                # NEW - Phase tracking
├── dspy_helm/                         # EXISTING - TO BE CONSOLIDATED in Phase 2
├── tests/                             # EXISTING - Test suite
├── scripts/                           # EXISTING - Utility scripts
├── OPTIMAL_CONFIG_PLAN.md             # THIS FILE
└── run.sh                             # EXISTING - Batch runner
```

### 1.2 Target Structure (After Phase 2)

```
gemini-cli-prompt-library/
├── commands/
├── dspy_integration/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── toml.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── architecture.py
│   │   ├── code_review.py
│   │   ├── documentation.py
│   │   ├── feature_dev.py
│   │   ├── improve.py
│   │   ├── security_review.py
│   │   └── unit_test.py
│   ├── framework/                     # NEW - CONSOLIDATED from dspy_helm/
│   │   ├── __init__.py
│   │   ├── providers/
│   │   ├── optimizers/
│   │   ├── evaluation/
│   │   ├── scenarios/
│   │   ├── data/
│   │   ├── config/
│   │   └── prompts/
│   └── optimizers/                    # TO BE DELETED
├── tests/
├── scripts/
└── OPTIMAL_CONFIG_PLAN.md
```

---

## Part 2: Phase 1 Implementation Summary

### 2.1 Files Created/Modified

| File | Status | Lines | Notes |
|------|--------|-------|-------|
| `dspy_integration/cli.py` | Created | ~350 | Unified CLI with all commands |
| `dspy_integration/toml.py` | Created | ~220 | TOMLManager, approach_toml() |
| `dspy_integration/modules/improve.py` | Created | ~140 | ImproveSignature, ImproveModule |
| `dspy_integration/__init__.py` | Modified | ~15 | Package exports |
| `dspy_integration/modules/__init__.py` | Modified | ~10 | Added "improve" registry |
| `dspy_integration/__main__.py` | Created | ~7 | Entry point |
| `dspy_integration/modules/unit_test.py` | Fixed | ~2 | self.generate → self.program |
| `dspy_integration/modules/documentation.py` | Fixed | ~2 | self.generate → self.program |

### 2.2 CLI Commands Implemented

```bash
# Working
python -m dspy_integration --help
python -m dspy_integration list [scenarios|modules|optimizers|all]
python -m dspy_integration compare "prompt" --approaches toml dspy
python -m dspy_integration evaluate "prompt"
python -m dspy_integration convert "prompt"
python -m dspy_integration optimize <scenario> --optimizer MIPROv2

# Placeholders (Phase 3)
python -m dspy_integration interactive
python -m dspy_integration sessions
```

### 2.3 Bugs Fixed

| File | Line | Bug | Fix |
|------|------|-----|-----|
| `modules/unit_test.py` | 32 | `self.generate` undefined in Optimizer | `self.generate` → `self.program` |
| `modules/documentation.py` | 34 | `self.generate` undefined in Optimizer | `self.generate` → `self.program` |

### 2.4 Known Issues (Post-Phase 1)

| Issue | Severity | Workaround |
|-------|----------|------------|
| `python -m dspy_integration list` fails | High | Use `python -m dspy_integration list all` |
| Missing `--output` arg in list parser | Medium | Always specify item (`all`, `scenarios`, etc.) |
| Pre-existing test imports failing | Low | Tests need late imports fixed (separate issue) |
| dspy_helm imports failing | Medium | Will be fixed in Phase 2 consolidation |

---

## Part 3: CLI Usage Notes

### 3.1 Installation Required

```bash
# Option 1: Set PYTHONPATH
cd /home/masum/github/gemini-cli-prompt-library
PYTHONPATH=. python -m dspy_integration list

# Option 2: Create pyproject.toml (recommended for Phase 4)
```

### 3.2 Command Reference

```bash
# Help
python -m dspy_integration --help

# List available items
python -m dspy_integration list                    # Fails (missing --output)
python -m dspy_integration list all                # Works
python -m dspy_integration list scenarios          # Works
python -m dspy_integration list modules            # Works
python -m dspy_integration list optimizers         # Works

# Improve a prompt (requires DSPy LM configured)
python -m dspy_integration improve "Your prompt"

# Compare approaches
python -m dspy_integration compare "Your prompt"
python -m dspy_integration compare "Your prompt" --approaches toml dspy

# Evaluate a prompt
python -m dspy_integration evaluate "Your prompt"

# Convert to DSPy module
python -m dspy_integration convert "Your prompt"

# Optimization (placeholder)
python -m dspy_integration optimize improve --optimizer MIPROv2

# Interactive mode (Phase 3)
python -m dspy_integration interactive "base prompt"

# Session management (Phase 3)
python -m dspy_integration sessions list
```

### 3.3 Output Formats

| Command | JSON Output | Text Output |
|---------|-------------|-------------|
| `list` | `--output json` | `--output text` (default) |
| `improve` | `--output json` | `--output text` (default) |
| `evaluate` | `--output json` (default) | `--output text` |
| `compare` | `--output json` | `--output text` (default) |
| `convert` | `--output json` | `--output text` (default) |

---

## Part 4: 5 Approaches Specification

### 4.1 Approach Matrix

| # | Name | Status | Score Range |
|---|------|--------|-------------|
| 1 | **TOML-based** | ✅ Implemented | 20-45 |
| 2 | **DSPy Basic** | ✅ Implemented | 25-48 |
| 3 | **MIPROv2** | ⚠️ Placeholder | N/A |
| 4 | **Bootstrap** | ⚠️ Placeholder | N/A |
| 5 | **Custom** | ⚠️ Placeholder | N/A |

### 4.2 Implemented: Approach 1 (TOML)

```python
# dspy_integration/toml.py
def approach_toml(prompt_text: str) -> Dict[str, Any]:
    manager = TOMLManager()
    improve_prompt = manager.load_prompt("improve")
    result = improve_prompt.execute(prompt_text)
    score = _calculate_score(prompt_text, result)
    return {"result": result, "score": score, "approach": "toml"}
```

### 4.3 Implemented: Approach 2 (DSPy Basic)

```python
# dspy_integration/modules/improve.py
class ImproveSignature(dspy.Signature):
    original_prompt = dspy.InputField(desc="The original prompt to improve")
    improved_prompt = dspy.OutputField(desc="The improved version of the prompt")
    changes_summary = dspy.OutputField(desc="Summary of the changes made")

class Improve(dspy.Module):
    def __init__(self):
        super().__init__()
        self.improve = dspy.ChainOfThought(ImproveSignature)
    
    def forward(self, original_prompt: str) -> dspy.Prediction:
        return self.improve(original_prompt=original_prompt)
```

---

## Part 5: Scoring System

### 5.1 Score Criteria

From `OPTIMAL_CONFIG_PLAN.md Part 4.3`:
- **Clarity** (0-10)
- **Specificity** (0-10)
- **Structure** (0-10)
- **Context** (0-10)
- **Output Format** (0-10)
- **Total**: 0-50

### 5.2 Current Implementation

Both TOML and DSPy approaches use `_calculate_score()` with heuristic scoring:
- Header presence (`#`, `##`)
- List formatting (`-`, `1.`)
- Code blocks (```)
- Specificity keywords
- Format specification
- Context keywords
- Step/phase indicators
- Example mentions
- Changes made

**Note:** Heuristic scoring is a placeholder. Full DSPy evaluation will be implemented in Phase 2.

---

## Part 6: Implementation Phases

### Phase 1: Foundation ✅ COMPLETE
| Task | File | Status | Notes |
|------|------|--------|-------|
| 1.1 | Create `cli.py` | ✅ Done | 11KB, all commands |
| 1.2 | Create `toml.py` | ✅ Done | 6KB, scoring included |
| 1.3 | Create `improve.py` | ✅ Done | 4KB, ChainOfThought |
| 1.4 | Update `modules/__init__.py` | ✅ Done | "improve" registered |
| 1.5 | Create `__main__.py` | ✅ Done | Entry point |
| 1.6 | Fix pre-existing bugs | ✅ Done | 2 files fixed |

### Phase 2: Framework Consolidation (Next)
| Task | File | Description |
|------|------|-------------|
| 2.1 | Create `framework/__init__.py` | Framework exports |
| 2.2 | Create `framework/scenarios/base.py` | Base scenario class |
| 2.3 | Create `framework/scenarios/improve.py` | ImproveScenario |
| 2.4 | Create `framework/scenarios/architecture.py` | ArchitectureScenario |
| 2.5 | Move `dspy_helm/providers/` | → `framework/providers/` |
| 2.6 | Move `dspy_helm/optimizers/` | → `framework/optimizers/` |
| 2.7 | Move `dspy_helm/evaluation/` | → `framework/evaluation/` |
| 2.8 | Move `dspy_helm/scenarios/` | → `framework/scenarios/` |
| 2.9 | Move `dspy_helm/data/` | → `framework/data/` |
| 2.10 | Move `dspy_helm/config/` | → `framework/config/` |
| 2.11 | Move `dspy_helm/prompts/` | → `framework/prompts/` |

### Phase 3: Interactive Features
| Task | File | Description |
|------|------|-------------|
| 3.1 | Update `cli.py` | Implement interactive() |
| 3.2 | Update `cli.py` | Add mipro/bootstrap approaches |
| 3.3 | Update `cli.py` | Add diff view |
| 3.4 | Update `cli.py` | Add persistence (~/.dspy_tuning/) |
| 3.5 | Update `cli.py` | Add save/load commands |
| 3.6 | Update `cli.py` | Add make-module command |

### Phase 4: Integration
| Task | File | Description |
|------|------|-------------|
| 4.1 | Create `pyproject.toml` | For pip install |
| 4.2 | Create `scripts/gemini_dspy_wrapper.py` | Shell-out wrapper |
| 4.3 | Update `GEMINI.md` | Add DSPy commands |
| 4.4 | Create `ARCHITECTURE.md` | Final architecture docs |

### Phase 5: Cleanup
| Task | Description |
|------|-------------|
| 5.1 | Delete `dspy_helm/` directory |
| 5.2 | Delete `dspy_integration/optimizers/` |
| 5.3 | Run full test suite |
| 5.4 | Verify all imports work |

---

## Part 7: CLI Bug Details

### 7.1 Missing `--output` Argument

**Issue:** The `list` subparser is missing `--output` argument.

**Current Code:**
```python
list_p = subparsers.add_parser("list", help="List available items")
list_p.add_argument("item", nargs="?", default="all", ...)
# Missing: list_p.add_argument("--output", ...)
```

**Error:**
```
Error: 'Namespace' object has no attribute 'output'
```

**Fix Required:** Add `--output` argument to list parser.

### 7.2 PYTHONPATH Requirement

**Issue:** `python -m dspy_integration` requires PYTHONPATH set.

**Workarounds:**
```bash
# Option 1: Set PYTHONPATH
PYTHONPATH=. python -m dspy_integration list all

# Option 2: Install in dev mode (needs pyproject.toml)
pip install -e .

# Option 3: Run from package directory
python -c "from dspy_integration.cli import main; ..."
```

**Recommended Fix (Phase 4):** Create `pyproject.toml` for proper installation.

---

## Part 8: Pre-Existing Issues (Not in Scope)

### 8.1 Test File Issues

**File:** `tests/test_modules.py`

**Issue:** Late imports inside test functions cause type checking errors.

**Example:**
```python
def test_signature_fields(self):
    from dspy_integration.modules.code_review import CodeReviewSignature
    # Late import causes "CodeReview" unknown symbol
```

**Status:** Pre-existing, not fixed in Phase 1.

### 8.2 dspy_helm Import Issues

**Files:** `dspy_helm/cli.py`, `dspy_helm/__init__.py`

**Issue:** Imports from non-existent modules.

```python
from dspy_helm.providers import ...  # Module doesn't exist
from dspy_helm.scenarios import ...  # Module doesn't exist
```

**Status:** Will be fixed when dspy_helm is consolidated into framework/ in Phase 2.

---

## Part 9: Verification Commands

### 9.1 Phase 1 Verification

```bash
cd /home/masum/github/gemini-cli-prompt-library

# Test CLI loads
PYTHONPATH=. python -m dspy_integration --help

# Test list command
PYTHONPATH=. python -m dspy_integration list all

# Test compare command
PYTHONPATH=. python -m dspy_integration compare "Write better code"

# Test imports
PYTHONPATH=. python -c "
from dspy_integration.modules import get_module_for_scenario
from dspy_integration.modules.improve import Improve
print('Imports work!')
"

# Test module registry
PYTHONPATH=. python -c "
from dspy_integration.modules import get_module_for_scenario, get_optimizer_for_scenario
m = get_module_for_scenario('improve')
o = get_optimizer_for_scenario('improve')
print(f'Module: {m}, Optimizer: {o}')
"
```

### 9.2 Expected Output After Phase 1

```
$ PYTHONPATH=. python -m dspy_integration list all
============================================================
AVAILABLE ITEMS
============================================================

Scenarios:
  - code_review
  - architecture
  - feature_dev
  - unit_test
  - documentation
  - security_review
  - improve

Modules:
  - code_review
  - architecture
  - feature_dev
  - unit_test
  - documentation
  - security_review
  - improve

Optimizers:
  - MIPROv2
  - BootstrapFewShot
  - BootstrapFewShotWithRandomSearch
============================================================
```

---

## Part 10: Next Steps (Phase 2)

### Immediate Tasks

1. **Fix CLI bug:** Add `--output` argument to list subparser
2. **Create framework structure:** Start with `framework/__init__.py`
3. **Consolidate one module:** Move `dspy_helm/providers/` first as proof of concept

### Phase 2 Deliverables

- `dspy_integration/framework/__init__.py`
- `dspy_integration/framework/scenarios/base.py`
- `dspy_integration/framework/scenarios/improve.py`
- Moved providers, optimizers, evaluation, scenarios, data, config, prompts
- Updated imports in `dspy_integration/__init__.py`

### Success Criteria for Phase 2

- [ ] `from dspy_integration.framework import ScenarioRegistry` works
- [ ] `from dspy_integration.framework.providers import get_provider_by_name` works
- [ ] `from dspy_integration.framework.optimizers import OptimizerRegistry` works
- [ ] All dspy_helm imports resolved
- [ ] CLI continues to work after consolidation

---

## Summary

| Aspect | Status |
|--------|--------|
| **Phase 1 (Foundation)** | ✅ Complete |
| **Phase 2 (Consolidation)** | ⏳ Next |
| **Phase 3 (Interactive)** | ⏳ Pending |
| **Phase 4 (Integration)** | ⏳ Pending |
| **Phase 5 (Cleanup)** | ⏳ Pending |
| **CLI Working** | ⚠️ Partial (bug in list command) |
| **DSPy Integration** | ✅ Basic (TOML + Basic) |
| **Framework Structure** | ❌ Not started |
| **dspy_helm Consolidated** | ❌ No |

---

## Related Documentation

- `OPTIMAL_CONFIG_PLAN.md` - This file
- `PHASE1_TODOS.md` - Phase 1 task tracking
- `PHASE2_TODOS.md` - Phase 2 task tracking
- `PHASE3_TODOS.md` - Phase 3 task tracking
- `PHASE4_TODOS.md` - Phase 4 task tracking

---

*Document Version: 2.0*  
*Last Updated: January 18, 2026*  
*Status: Phase 1 Complete - Beginning Phase 2*
