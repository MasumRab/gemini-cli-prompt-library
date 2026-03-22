# Master TODO List - OPTIMAL_CONFIG_PLAN.md Implementation

**Document**: OPTIMAL_CONFIG_PLAN.md
**Status**: In Progress
**Last Updated**: January 18, 2026

---

## Quick Start

This implementation is divided into 5 phases. Complete phases in order.

### Phase 1: Foundation (Days 1-2)
- [ ] Task 1.1: Create cli.py
- [ ] Task 1.2: Create toml.py
- [ ] Task 1.3: Create improve.py
- [ ] Task 1.4: Update modules/__init__.py
- **File**: `dspy_integration/PHASE1_TODOS.md`

### Phase 2: Framework Consolidation (Days 2-3)
- [ ] Task 2.1: Create framework/__init__.py
- [ ] Task 2.2: Create scenarios/improve.py
- [ ] Task 2.3: Create scenarios/architecture.py
- [ ] Tasks 2.4-2.10: Move dspy_helm/ to framework/
- **File**: `dspy_integration/PHASE2_TODOS.md`

### Phase 3: Interactive Features (Days 3-5)
- [ ] Task 3.1: Add interactive mode to cli.py
- [ ] Task 3.2: Implement 5 approaches
- [ ] Task 3.3: Add comparison table
- [ ] Task 3.4: Add diff view
- [ ] Task 3.5: Add persistence
- [ ] Task 3.6: Add make-module
- **File**: `dspy_integration/PHASE3_TODOS.md`

### Phase 4: Integration (Days 5-6)
- [ ] Task 4.1: Create gemini_dspy_wrapper.py
- [ ] Task 4.2: Update GEMINI.md
- [ ] Task 4.3: Create ARCHITECTURE.md
- [ ] Task 4.4: Update meta-dspy.md
- **File**: `dspy_integration/PHASE4_TODOS.md`

### Phase 5: Cleanup (Day 7)
- [ ] Delete dspy_helm/ directory
- [ ] Delete dspy_integration/optimizers/
- [ ] Delete external /home/masum/github/dspy_integration/
- [ ] Run full test suite
- [ ] Verify all imports

---

## Pre-Implementation Checklist

Before starting, ensure:

- [ ] OPTIMAL_CONFIG_PLAN.md is saved
- [ ] Backup of current state (git commit)
- [ ] No uncommitted changes in dspy_helm/ or dspy_integration/
- [ ] Python environment ready
- [ ] DSPy installed: `pip install dspy-ai`

---

## Codebase Files to Modify (4 files)

| File | Changes Required | Status |
|------|------------------|--------|
| `dspy_integration/__init__.py` | Add framework exports, improve imports | [ ] Pending |
| `dspy_integration/modules/__init__.py` | Add "improve" to registry | [ ] Pending |
| `GEMINI.md` | Add /dspy:* commands | [ ] Pending |
| `meta-dspy.md` | Update architecture references | [ ] Pending |

---

## Codebase Files to Create (13 files)

| File | Phase | Status |
|------|-------|--------|
| `dspy_integration/cli.py` | 1 | [ ] Pending |
| `dspy_integration/toml.py` | 1 | [ ] Pending |
| `dspy_integration/modules/improve.py` | 1 | [ ] Pending |
| `dspy_integration/framework/__init__.py` | 2 | [ ] Pending |
| `dspy_integration/framework/scenarios/improve.py` | 2 | [ ] Pending |
| `dspy_integration/framework/scenarios/architecture.py` | 2 | [ ] Pending |
| `dspy_integration/framework/data/architecture.jsonl` | 2 | [ ] Pending |
| `dspy_integration/framework/prompts/__init__.py` | 2 | [ ] Pending |
| `dspy_integration/framework/prompts/toml_converter.py` | 2 | [ ] Pending |
| `dspy_integration/framework/config/__init__.py` | 2 | [ ] Pending |
| `scripts/gemini_dspy_wrapper.py` | 4 | [ ] Pending |
| `ARCHITECTURE.md` | 4 | [ ] Pending |
| `OPTIMAL_CONFIG_PLAN.md` | - | [x] Complete |

---

## Codebase Files to Delete (3 items)

| Item | Phase | Reason |
|------|-------|--------|
| `dspy_helm/` directory | 5 | Consolidated into framework/ |
| `dspy_integration/optimizers/` | 5 | Replaced by framework/optimizers/ |
| `/home/masum/github/dspy_integration/` | 5 | Outdated duplicate |

---

## Verification Commands

After each phase, run these commands:

```bash
# Phase 1
python -m dspy_integration list
python -m dspy_integration improve "test prompt"

# Phase 2
python -c "from dspy_integration.framework import ScenarioRegistry; print(ScenarioRegistry.list())"

# Phase 3
python -m dspy_integration interactive --help
python -m dspy_integration sessions

# Phase 4
python -c "from scripts.gemini_dspy_wrapper import main; print('Wrapper loads')"

# Phase 5
python -m pytest tests/ -v
```

---

## Bug Fixes Required (During Implementation)

| File | Issue | Line | Fix |
|------|-------|------|-----|
| `documentation.py` | self.generate → self.program | 34 | Bug fix |
| `unit_test.py` | self.generate → self.program | 32 | Bug fix |

---

## Related Documentation

- `OPTIMAL_CONFIG_PLAN.md` - Main implementation plan
- `IMPLEMENTATION_PLAN.md` - Original prompt systems plan
- `DSPY_HELM_IMPLEMENTATION_PLAN.md` - Original dspy-helm plan
- `META_TODO.md` - Meta-todo for prompt systems integration

---

## Progress Tracking

| Phase | Tasks | Completed | Status |
|-------|-------|-----------|--------|
| 1 | 4 | 0 | [ ] Not Started |
| 2 | 10 | 0 | [ ] Not Started |
| 3 | 6 | 0 | [ ] Not Started |
| 4 | 4 | 0 | [ ] Not Started |
| 5 | 5 | 0 | [ ] Not Started |
| **Total** | **29** | **0** | **0%** |

---

*This file is auto-generated from OPTIMAL_CONFIG_PLAN.md*
*Update: January 18, 2026*
