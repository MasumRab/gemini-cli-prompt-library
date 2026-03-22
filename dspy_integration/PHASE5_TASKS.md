# Phase 5: Cleanup & Finalization

**Status**: NOT STARTED  
**Started**: -  
**Completed**: -  
**Duration Estimate**: 1 day

---

## Overview

Clean up obsolete directories, run full test suite, verify all imports, and prepare for release.

## Task Graph

```
SEQUENTIAL TRACK A: Directory Cleanup
├── 5.1.1 Delete dspy_helm/ (after consolidation) [DEPENDS: Phase 2]
├── 5.1.2 Delete dspy_integration/optimizers/ [DEPENDS: Phase 2]
└── 5.1.3 Clean up orphaned files [INDEPENDENT]

SEQUENTIAL TRACK B: Testing
├── 5.2.1 Run full test suite [INDEPENDENT]
├── 5.2.2 Fix any failing tests [DEPENDS: 5.2.1]
└── 5.2.3 Add missing tests [DEPENDS: 5.2.2]

SEQUENTIAL TRACK C: Verification
├── 5.3.1 Verify all imports work [INDEPENDENT]
├── 5.3.2 Verify CLI commands work [INDEPENDENT]
└── 5.3.3 Performance benchmark [INDEPENDENT]

SEQUENTIAL TRACK D: Release Prep
├── 5.4.1 Update version in pyproject.toml [INDEPENDENT]
├── 5.4.2 Update CHANGELOG.md [INDEPENDENT]
└── 5.4.3 Create release notes [INDEPENDENT]
```

---

## Tasks

### 5.1 Directory Cleanup (Track A)

#### 5.1.1 Delete dspy_helm/
```
Status: PENDING
Priority: HIGH
Depends: Phase 2 Complete
Assign: -
Est: 10 min

After consolidation (moved to framework/):
rm -rf dspy_helm/

Verify:
- No imports reference dspy_helm
- No scripts use dspy_helm
- tests/ updated if needed
```

#### 5.1.2 Delete dspy_integration/optimizers/
```
Status: PENDING
Priority: HIGH
Depends: Phase 2 Complete
Assign: -
Est: 5 min

After consolidation:
rm -rf dspy_integration/optimizers/

Verify:
- framework/optimizers/ exists and works
- No imports reference optimizers/
```

#### 5.1.3 Clean up orphaned files
```
Status: PENDING
Priority: MEDIUM
Depends: None
Assign: -
Est: 30 min

Find and remove orphaned files:
- Find files not referenced by any import
- Find duplicate documentation
- Find obsolete test files

Command:
find . -type f -name "*.py" -o -name "*.md" | xargs grep -l "dspy_helm" 2>/dev/null
```

---

### 5.2 Testing (Track B)

#### 5.2.1 Run full test suite
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 10 min

Command:
pytest tests/ -v --tb=short

Expected: All tests pass

Categories:
- test_modules.py (module tests)
- test_cli.py (CLI tests)
- test_integration.py (integration tests)
- test_edge_cases.py (edge case tests)
- test_dspy_helm.py (framework tests)
```

#### 5.2.2 Fix any failing tests
```
Status: PENDING
Priority: HIGH
Depends: 5.2.1
Assign: -
Est: Variable

For each failing test:
1. Identify root cause
2. Fix the code OR update test
3. Re-run to verify

Common issues:
- Import paths changed
- API signatures changed
- Mock objects need updates
```

#### 5.2.3 Add missing tests
```
Status: PENDING
Priority: MEDIUM
Depends: 5.2.2
Assign: -
Est: 1 hour

Add tests for new features:
- test_registry.py (CommandRegistry)
- test_dispatcher.py (IntelligentDispatcher)
- test_hash_embedder.py (HashEmbedder)
- test_interactive.py (REPL mode)
- test_agent_mode.py (Agent skills)

Coverage target: 80%
```

---

### 5.3 Verification (Track C)

#### 5.3.1 Verify all imports work
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 15 min

Test all documented imports:

from dspy_integration import get_module_for_scenario
from dspy_integration.framework import ScenarioRegistry
from dspy_integration.framework import OptimizerRegistry
from dspy_integration.framework import ProviderChain
from dspy_integration.framework import CommandRegistry
from dspy_integration.framework import IntelligentDispatcher
from dspy_integration.framework.providers import get_provider_by_name
from dspy_integration.framework.optimizers import OptimizerRegistry
```

#### 5.3.2 Verify CLI commands work
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 15 min

Test all commands:

python -m dspy_integration --help
python -m dspy_integration list
python -m dspy_integration list all
python -m dspy_integration list scenarios
python -m dspy_integration list modules
python -m dspy_integration list optimizers
python -m dspy_integration improve "test prompt"
python -m dspy_integration compare "test prompt"
python -m dspy_integration evaluate "test prompt"
python -m dspy_integration convert "test prompt"
python -m dspy_integration dispatch "fix login bug"
python -m dspy_integration --robot --json list
```

#### 5.3.3 Performance benchmark
```
Status: PENDING
Priority: LOW
Depends: None
Assign: -
Est: 30 min

Benchmark key operations:

1. CLI startup time
   Target: <500ms

2. List command
   Target: <100ms

3. Improve command (TOML approach)
   Target: <200ms

4. Improve command (DSPy approach)
   Target: <2s (LM call)

5. Compare command
   Target: <500ms

6. Search (if implemented)
   Target: <60ms (CASS target)

Create benchmark script: scripts/benchmark.py
```

---

### 5.4 Release Prep (Track D)

#### 5.4.1 Update version in pyproject.toml
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 5 min

Create or update pyproject.toml:

[project]
name = "gemini-cli-prompt-library"
version = "3.0.0"
description = "DSPy-powered prompt engineering toolkit"
readme = "README.md"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "black", "ruff"]
semantic = ["fastembed"]  # Optional for ML embeddings

[project.scripts]
dspy-integration = "dspy_integration.cli:main"
```

#### 5.4.2 Update CHANGELOG.md
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 30 min

Create or update CHANGELOG.md:

# Changelog

## [3.0.0] - 2026-01-18

### Added
- Framework consolidation (dspy_helm → framework/)
- Intelligent Dispatcher for natural language routing
- Command Registry for 41 commands
- 5 improvement approaches (TOML, DSPy, MIPROv2, Bootstrap, Custom)
- HashEmbedder for zero-dep semantic search
- Edge N-Gram indexing for fast prefix search
- Interactive REPL mode with history
- Agent mode with proactive suggestions
- Self-correction skills for error recovery
- Robot/JSON mode for AI automation
- Forgiving CLI parsing for AI agents

### Changed
- Improved module signatures with Optional type hints
- Added security_review module
- Updated 24 TOML command files

### Removed
- dspy_helm/ directory (consolidated)
- dspy_integration/optimizers/ (consolidated)
```

#### 5.4.3 Create release notes
```
Status: PENDING
Priority: MEDIUM
Depends: None
Assign: -
Est: 15 min

Create RELEASE_NOTES.md:

# Release 3.0.0

## What's New

### Intelligent Dispatcher
Natural language routing for commands:
```bash
cass dispatch "fix my login bug"
```

### 5 Improvement Approaches
Choose your approach:
- `toml` - Fast, template-based
- `dspy` - ChainOfThought reasoning
- `mipro` - Full MIPROv2 optimization
- `bootstrap` - Lightweight BootstrapFewShot
- `custom` - Focused refinement

### Agent Mode
Autonomous agent with self-correction:
```bash
cass improve "fix bug" --agent-mode --auto-correct
```

## Upgrade from 2.x

No breaking changes. New features are additive.

## Full Changelog

See CHANGELOG.md
```

---

## Deliverables

After Phase 5:
- [ ] dspy_helm/ deleted
- [ ] dspy_integration/optimizers/ deleted
- [ ] All tests pass (80%+ coverage)
- [ ] All documented imports work
- [ ] All CLI commands verified
- [ ] Performance benchmarks documented
- [ ] pyproject.toml created
- [ ] CHANGELOG.md updated
- [ ] RELEASE_NOTES.md created

## Final Project Structure

```
gemini-cli-prompt-library/
├── commands/                          # 41 TOML prompts
├── dspy_integration/
│   ├── __init__.py                    # Package exports
│   ├── __main__.py                    # CLI entry point
│   ├── cli.py                         # Unified CLI
│   ├── toml.py                        # TOML manager
│   ├── modules/                       # DSPy modules
│   │   ├── __init__.py
│   │   ├── architecture.py
│   │   ├── code_review.py
│   │   ├── documentation.py
│   │   ├── feature_dev.py
│   │   ├── improve.py
│   │   ├── security_review.py
│   │   └── unit_test.py
│   ├── framework/                     # Consolidated
│   │   ├── __init__.py
│   │   ├── providers/
│   │   ├── optimizers/
│   │   ├── evaluation/
│   │   ├── scenarios/
│   │   ├── data/
│   │   └── prompts/
│   ├── semantic/                      # CASS patterns
│   │   ├── hash_embedder.py
│   │   ├── edge_ngram.py
│   │   └── vector_index.py
│   ├── interactive/                   # REPL
│   │   ├── session.py
│   │   ├── history.py
│   │   └── completer.py
│   ├── ui/                            # Rich UI
│   │   ├── menu.py
│   │   ├── recommendation.py
│   │   └── progression.py
│   └── agents/                        # Agent skills
│       ├── suggester.py
│       ├── self_correct.py
│       ├── error_analyzer.py
│       └── prompt_rewriter.py
├── tests/                             # Test suite
├── scripts/                           # Utility scripts
├── docs/                              # Documentation
├── pyproject.toml                     # Package config
├── CHANGELOG.md                       # Changelog
└── README.md                          # Project readme
```

## Version Bump

From: 2.x (Phase 1 only)  
To: 3.0.0 (Full implementation)

## Next Steps After Phase 5

1. Publish to PyPI (optional)
2. Create GitHub release
3. Update documentation website
4. Announce on social media
5. Collect user feedback
6. Plan version 3.1
