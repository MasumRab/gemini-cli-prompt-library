# Phase 2: Framework Consolidation + Dispatcher

**Status**: NOT STARTED  
# TODO: Update status of tasks to reflect completion of framework consolidation and dispatcher refactor progress.
**Started**: -  
**Completed**: -  
**Duration Estimate**: 2-3 days

---

## Overview

Consolidate dspy_helm into framework/ and add Intelligent Dispatcher for natural language routing.

## Task Graph

```
PARALLEL TRACK A: Framework Structure
├── 2.1.1 Create framework/__init__.py [INDEPENDENT]
├── 2.1.2 Create framework/providers/ [INDEPENDENT]
├── 2.1.3 Create framework/optimizers/ [INDEPENDENT]
└── 2.1.4 Create framework/evaluation/ [INDEPENDENT]

PARALLEL TRACK B: Dispatcher Components  
├── 2.2.1 Create framework/registry.py [INDEPENDENT]
├── 2.2.2 Create framework/dispatcher.py [DEPENDS: 2.2.1]
└── 2.2.3 Add CLI dispatcher integration [DEPENDS: 2.2.2]

PARALLEL TRACK C: CLI Improvements
├── 2.3.1 Add forgiving CLI parsing [INDEPENDENT]
├── 2.3.2 Add robot mode (--robot, --json) [INDEPENDENT]
└── 2.3.3 Complete unimplemented CLI methods [DEPENDS: 2.2.3]

PARALLEL TRACK D: Consolidation
├── 2.4.1 Move dspy_helm/providers → framework/ [INDEPENDENT]
├── 2.4.2 Move dspy_helm/optimizers → framework/ [INDEPENDENT]
├── 2.4.3 Move dspy_helm/evaluation → framework/ [INDEPENDENT]
├── 2.4.4 Move dspy_helm/scenarios → framework/ [INDEPENDENT]
├── 2.4.5 Move dspy_helm/data → framework/ [INDEPENDENT]
└── 2.4.6 Update imports across codebase [DEPENDS: ALL ABOVE]
```

---

## Tasks

### 2.1 Framework Structure (Track A)

#### 2.1.1 Create framework/__init__.py
```
Status: COMPLETED
Priority: HIGH
Depends: None
Assign: -
Est: 30 min

Create framework/__init__.py with exports:
- from .registry import CommandRegistry, get_command
- from .dispatcher import IntelligentDispatcher
- from .providers import get_provider
- from .optimizers import get_optimizer
- from .evaluation import Evaluator
```

#### 2.1.2 Create framework/providers/
```
Status: COMPLETED
Priority: MEDIUM
Depends: None
Assign: -
Est: 1 hour

Create framework/providers/__init__.py
Copy from dspy_helm/providers/:
- base.py
- gemini.py
- groq.py
- huggingface.py
- openrouter.py
- opencode.py
- opencode_zen.py
- qwen.py
- puter.py
```

#### 2.1.3 Create framework/optimizers/
```
Status: COMPLETED
Priority: MEDIUM
Depends: None
Assign: -
Est: 1 hour

Create framework/optimizers/__init__.py
Copy from dspy_helm/optimizers/:
- base.py
- mipro_v2.py
- bootstrap.py
```

#### 2.1.4 Create framework/evaluation/
```
Status: COMPLETED
Priority: MEDIUM
Depends: None
Assign: -
Est: 45 min

Create framework/evaluation/__init__.py
Copy from dspy_helm/evaluation/:
- evaluate.py
```

---

### 2.2 Dispatcher Components (Track B)

#### 2.2.1 Create framework/registry.py
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 2 hours

CommandRegistry class:
- Auto-discovers 41 commands from commands/
- Loads metadata from TOML files
- Provides search() by keyword
- Provides list_by_category()
- Provides get_command()

Tests:
- test_registry.py (4 tests)
```

#### 2.2.2 Create framework/dispatcher.py
```
Status: PENDING
Priority: HIGH
Depends: 2.2.1
Assign: -
Est: 3 hours

IntelligentDispatcher class:
- dispatch(user_request) → command match
- _keyword_match() for basic selection
- _refine_prompt() for prompt optimization
- _find_alternatives() for alternatives

Tests:
- test_dispatcher.py (5 tests)
```

#### 2.2.3 Add CLI dispatcher integration
```
Status: PENDING
Priority: HIGH
Depends: 2.2.2
Assign: -
Est: 1 hour

In cli.py:
- Add `dispatch` command
- Add `improve --smart` flag that uses dispatcher
- Update `improve` to show alternatives
```

---

### 2.3 CLI Improvements (Track C)

#### 2.3.1 Add forgiving CLI parsing
```
Status: PENDING
Priority: MEDIUM
Depends: None
Assign: -
Est: 1 hour

In cli.py:
- normalize_args() function
- Single-dash to double-dash conversion
- Flag typo correction (edit distance <= 2)
- Command alias resolution (find→search, ls→stats)
```

#### 2.3.2 Add robot mode
```
Status: PENDING
Priority: MEDIUM
Depends: None
Assign: -
Est: 1 hour

Add robot/AI mode flags:
- --robot: Enable robot mode
- --robot-format: json, jsonl, compact
- --robot-meta: Include performance metadata
- --fields: Comma-separated fields
- --max-content-length: Truncation
- --max-tokens: Soft budget
```

#### 2.3.3 Complete unimplemented CLI methods
```
Status: PENDING
Priority: MEDIUM
Depends: 2.2.3
Assign: -
Est: 2 hours

Complete these methods in DSPyIntegrationCLI:
- interactive() [currently placeholder]
- sessions() [currently placeholder]
- optimize() [currently returns placeholder]
- compare() [already works]
```

---

### 2.4 Consolidation (Track D)

#### 2.4.1 Move dspy_helm/providers → framework/
```
Status: COMPLETED
Priority: MEDIUM
Depends: None
Assign: -
Est: 30 min

Command:
git mv dspy_helm/providers framework/
```

#### 2.4.2 Move dspy_helm/optimizers → framework/
```
Status: COMPLETED
Priority: MEDIUM
Depends: None
Assign: -
Est: 30 min

Command:
git mv dspy_helm/optimizers framework/
```

#### 2.4.3 Move dspy_helm/evaluation → framework/
```
Status: COMPLETED
Priority: MEDIUM
Depends: None
Assign: -
Est: 30 min

Command:
git mv dspy_helm/evaluation framework/
```

#### 2.4.4 Move dspy_helm/scenarios → framework/
```
Status: COMPLETED
Priority: MEDIUM
Depends: None
Assign: -
Est: 30 min

Command:
git mv dspy_helm/scenarios framework/
```

#### 2.4.5 Move dspy_helm/data → framework/
```
Status: COMPLETED
Priority: MEDIUM
Depends: None
Assign: -
Est: 30 min

Command:
git mv dspy_helm/data framework/
```

#### 2.4.6 Update imports across codebase
```
Status: COMPLETED
Priority: HIGH
Depends: ALL 2.4.1-2.4.5
Assign: -
Est: 2 hours

Update imports in:
- dspy_helm/__init__.py
- dspy_helm/cli.py
- tests/*.py
- scripts/*.py

Search for:
- from dspy_helm.providers import
- from dspy_helm.optimizers import
- from dspy_helm.evaluation import
```

---

## Deliverables

After Phase 2:
- [ ] `dspy_integration/framework/` exists with all subdirectories
- [ ] `from dspy_integration.framework import CommandRegistry` works
- [ ] `from dspy_integration.framework import IntelligentDispatcher` works
- [ ] `python -m dspy_integration dispatch "fix my login bug"` works
- [ ] `python -m dspy_integration --robot --json list` works
- [ ] `dspy_helm/` directory is empty/removed

## Dependencies

- Python 3.11+
- dspy-ai
- tomli (for TOML parsing)

## Notes

- Run tasks in parallel where dependencies allow
- Test each subtask before moving to next
- Update INTEGRATED_ENHANCEMENT_PLAN.md as tasks complete
