# Optimal Configuration Implementation Plan

**Version**: 1.0  
**Date**: January 18, 2026  
**Updated**: January 18, 2026 (Added acceptance criteria and subtasks)  
**Mode**: Implementation Mode (Building Phase)

---

## Executive Summary

This plan implements the **Optimal Configuration** for gemini-cli-prompt-library which includes:

1. **Full DSPy-HELM Consolidation** - Merge `dspy_helm/` → `dspy_integration/framework/`
2. **Unified Interactive CLI** - Single entry point `dspy_integration/cli.py`
3. **Interactive Tuning Workflow** - 5 approaches, comparison, persistence, dual Gemini modes
4. **All 6 Feature Choices** - As scored and selected in the planning process

**Expected Outcome:** A unified, fully-featured DSPy prompt engineering system accessible from both terminal and Gemini CLI with interactive tuning capabilities.

---

## Part 1: Consolidation Plan

### 1.1 Directory Structure After Consolidation

```
gemini-cli-prompt-library/
├── commands/                          # EXISTING - TOML prompts (40+ files)
├── dspy_integration/                  # UNIFIED - All DSPy functionality
│   ├── __init__.py                    # Root exports
│   ├── cli.py                         # NEW: Unified CLI entry point
│   ├── toml.py                        # NEW: TOML wrapper with DSPy fallback
│   ├── modules/                       # EXISTING - Core modules
│   │   ├── __init__.py                # Factory functions, registry
│   │   ├── architecture.py
│   │   ├── api_design.py              # NEW (from dspy_helm/scenarios/)
│   │   ├── code_review.py
│   │   ├── documentation.py
│   │   ├── feature_dev.py
│   │   ├── improve.py                 # NEW
│   │   ├── security_review.py
│   │   └── unit_test.py
│   ├── framework/                     # NEW: Merged from dspy_helm/
│   │   ├── __init__.py                # Framework exports
│   │   ├── providers/                 # From dspy_helm/providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── groq.py
│   │   │   ├── huggingface.py
│   │   │   ├── opencode_zen.py
│   │   │   ├── openrouter.py
│   │   │   ├── gemini.py
│   │   │   └── qwen.py
│   │   ├── optimizers/                # From dspy_helm/optimizers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── mipro_v2.py
│   │   │   └── bootstrap.py
│   │   ├── evaluation/                # From dspy_helm/eval/
│   │   │   ├── __init__.py
│   │   │   └── evaluate.py
│   │   ├── scenarios/                 # From dspy_helm/scenarios/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── api_design.py
│   │   │   ├── architecture.py        # NEW
│   │   │   ├── documentation.py
│   │   │   ├── security_review.py
│   │   │   ├── unit_test.py
│   │   │   └── improve.py             # NEW
│   │   ├── data/                      # From dspy_helm/data/
│   │   │   ├── api_design.jsonl
│   │   │   ├── architecture.jsonl     # NEW
│   │   │   ├── documentation.jsonl
│   │   │   ├── security_review.jsonl
│   │   │   └── unit_test.jsonl
│   │   ├── config/                    # From dspy_helm/config/
│   │   │   ├── __init__.py
│   │   │   └── providers.py
│   │   └── prompts/                   # From dspy_helm/prompts/
│   │       ├── __init__.py
│   │       └── toml_converter.py
│   ├── optimizers/                    # TO BE DELETED (replaced by framework/optimizers/)
│   │   ├── __init__.py
│   │   └── optimize_module.py
│   └── pycache/
├── tests/                             # EXISTING - Test suite
├── scripts/                           # EXISTING - Utility scripts
├── docs/                              # EXISTING - Documentation
├── ARCHITECTURE.md                    # NEW - Architecture documentation
├── meta-dspy.md                       # UPDATE - With consolidation info
├── OPTIMAL_CONFIG_PLAN.md             # THIS FILE
├── IMPLEMENTATION_PLAN.md             # KEEP - Original prompt systems plan
├── DSPY_HELM_IMPLEMENTATION_PLAN.md   # KEEP - Original dspy-helm plan
└── run.sh                             # EXISTING - Batch runner
```

### 1.2 Files to CREATE (13 files)

| File | Lines | Purpose |
|------|-------|---------|
| `dspy_integration/cli.py` | ~400 | Unified CLI with tune/compare/interactive |
| `dspy_integration/toml.py` | ~150 | TOML wrapper with DSPy fallback |
| `dspy_integration/modules/improve.py` | ~60 | ImproveModule for DSPy |
| `dspy_integration/framework/__init__.py` | ~80 | Framework exports |
| `dspy_integration/framework/scenarios/improve.py` | ~100 | ImproveScenario for evaluation |
| `dspy_integration/framework/scenarios/architecture.py` | ~120 | ArchitectureScenario |
| `dspy_integration/framework/data/architecture.jsonl` | ~20 | Test data (10-20 cases) |
| `dspy_integration/framework/prompts/__init__.py` | ~50 | Prompt exports |
| `dspy_integration/framework/prompts/toml_converter.py` | ~100 | TOML conversion |
| `dspy_integration/framework/config/__init__.py` | ~50 | Config exports |
| `scripts/gemini_dspy_wrapper.py` | ~80 | Gemini CLI shell-out |
| `ARCHITECTURE.md` | ~200 | Architecture documentation |
| `OPTIMAL_CONFIG_PLAN.md` | ~500 | This file (plan documentation) |

### 1.3 Files to MODIFY (4 files)

| File | Changes |
|------|---------|
| `dspy_integration/__init__.py` | Add framework exports, improve imports |
| `dspy_integration/modules/__init__.py` | Add `improve` to `_SCENARIOS_TO_MODULES` |
| `GEMINI.md` | Add DSPy commands section (`/dspy:*` commands) |
| `meta-dspy.md` | Update with new architecture, remove dspy_helm references |

### 1.4 Files to DELETE (3 items)

| Item | Reason |
|------|--------|
| `dspy_helm/` directory | Consolidated into `dspy_integration/framework/` |
| `dspy_integration/optimizers/` directory | Replaced by `framework/optimizers/` |
| `/home/masum/github/dspy_integration/` external duplicate | Outdated, consolidated |

---

## Part 2: CLI Commands Specification

### 2.1 Terminal Commands

```bash
# Interactive session
python -m dspy_integration interactive

# Single attempts
python -m dspy_integration improve "base prompt"
python -m dspy_integration evaluate "prompt"
python -m dspy_integration convert "prompt"

# Optimization
python -m dspy_integration optimize <scenario> --optimizer MIPROv2

# Comparison
python -m dspy_integration compare "base prompt"
python -m dspy_integration compare "base prompt" --approaches toml,dspy,mipro

# Listing
python -m dspy_integration list scenarios
python -m dspy_integration list modules
python -m dspy_integration list optimizers

# Session management
python -m dspy_integration sessions          # List saved sessions
python -m dspy_integration load <name>       # Load saved session
python -m dspy_integration delete <name>     # Delete saved session
```

### 2.2 Inside Interactive Session

```
$ python -m dspy_integration interactive
DSPy Interactive Tuning Session
─────────────────────────────────────
Base: "Write better code"

Commands:
  try <approach> [args]  - Try improvement approach
  try all                - Try all approaches
  compare                - Compare all attempts
  diff <num1> <num2>     - Show diff between two attempts
  pick <num>             - Select best version
  save <name>            - Save session to file
  load <name>            - Load saved session
  sessions               - List saved sessions
  make-module            - Convert to DSPy module
  quit                   - Exit (prompts to save)

> try improve
Score: 32/50
Result: "Write clear, well-structured code..."

> try mipro
[Running MIPROv2 optimization...]
Score: 44/50
Result: "Write production-quality code with..."

> compare
┌─────┬──────────┬─────────────────────────────────┬───────┐
│ #   │ Approach  │ Result                          │ Score │
├─────┼──────────┼─────────────────────────────────┼───────┤
│ 1   │ improve  │ "Write clear, well-structured..."│ 32/50 │
│ 2   │ mipro    │ "Write production-quality code..."│ 44/50 │
└─────┴──────────┴─────────────────────────────────┴───────┘

> pick 2
Selected: MIPROv2 optimized version

> save my-improved-prompt
Saved: ~/.dspy_tuning/my-improved-prompt.json

> quit
Save session? [y/n]: y
Saved session to: ~/.dspy_tuning/session-20260118.json
```

### 2.3 Gemini CLI Commands

```
# Interactive session (embedded)
> /dspy:interactive "Write better code"
  [Enters interactive session with base prompt]
  [...do work...]
  [Results returned when user quits]

# Single-shot commands
> /dspy:improve "Your prompt"
  [Returns improved prompt immediately]

> /dspy:evaluate "Your prompt"
  [Returns score and analysis]

> /dspy:compare "Your prompt"
  [Returns comparison table]

> /dspy:optimize security_review --optimizer MIPROv2
  [Runs optimization, returns result]

# Session management
> /dspy:list scenarios
> /dspy:sessions
> /dspy:load <name>
```

---

## Part 3: 5 Approaches Specification

### 3.1 Approach Matrix

| # | Name | Command | Speed | Quality | Use Case |
|---|------|---------|-------|---------|----------|
| 1 | **TOML-based** | `try improve` | ⚡ Fast | 📊 28-35 | Quick checks, simple prompts |
| 2 | **DSPy Basic** | `try dspy` | ⚡ Fast | 📊 32-38 | Standard improvement |
| 3 | **MIPROv2** | `try mipro` | 🐢 Slow | 📊 40-48 | Best quality, thorough optimization |
| 4 | **Bootstrap** | `try bootstrap` | 🐢 Slow | 📊 38-45 | Good balance, fewer API calls |
| 5 | **Custom** | `try refine --focus clarity --examples 3` | ⚡⚡ Varies | 📊 Varies | Targeted refinement |

### 3.2 Approach Details

#### Approach 1: TOML-based (commands/prompts/improve.toml)
```python
# Implementation: toml.py
def approach_toml(prompt):
    toml_prompt = load_prompt("improve")
    result = toml_prompt.execute(prompt)
    score = evaluate_score(result)  # From evaluate.toml
    return {"result": result, "score": score, "approach": "toml"}
```

#### Approach 2: DSPy Basic (dspy_integration/modules/improve.py)
```python
# Implementation: improve.py
class ImproveSignature(dspy.Signature):
    original_prompt = dspy.InputField(desc="Original prompt to improve")
    improved_prompt = dspy.OutputField(desc="Improved prompt")
    changes_summary = dspy.OutputField(desc="Summary of changes")

class Improve(dspy.Module):
    def __init__(self):
        super().__init__()
        self.improve = dspy.ChainOfThought(ImproveSignature)
    
    def forward(self, original_prompt):
        return self.improve(original_prompt=original_prompt)
```

#### Approach 3: MIPROv2 Optimization
```python
# Implementation: cli.py
def approach_mipro(prompt):
    module = get_module_for_scenario("improve")
    trainset, valset = load_improve_data()
    optimizer = OptimizerRegistry.create("MIPROv2", metric=improve_metric)
    optimized = optimizer.compile(module, trainset, valset)
    result = optimized(original_prompt=prompt)
    score = evaluate_score(result)
    return {"result": result, "score": score, "approach": "mipro"}
```

#### Approach 4: BootstrapFewShot
```python
# Similar to MIPRO but uses BootstrapFewShot optimizer
# Fewer API calls, faster than MIPRO
```

#### Approach 5: Custom Refinement
```python
# Implementation: cli.py
def approach_custom(prompt, focus="clarity", examples=0):
    # Focus options: clarity, specificity, structure, context, output
    # Examples: 0-5 few-shot examples
    refined_prompt = refine_with_focus(prompt, focus, examples)
    return {"result": refined_prompt, "approach": "custom", "focus": focus}
```

---

## Part 4: Comparison & Diff View

### 4.1 Table View

```
┌─────┬──────────┬─────────────────────────────────┬───────┐
│ #   │ Approach  │ Result                          │ Score │
├─────┼──────────┼─────────────────────────────────┼───────┤
│ 1   │ TOML     │ "Write clear, well-structured..."│ 32/50 │
│ 2   │ DSPy     │ "Write production-quality code..."│ 38/50 │
│ 3   │ MIPROv2  │ "Write maintainable code with..." │ 44/50 │
│ 4   │ Bootstrap│ "Write clean, tested code with..."│ 41/50 │
└─────┴──────────┴─────────────────────────────────┴───────┘
```

### 4.2 Diff View

```
diff #1 (TOML) → #3 (MIPROv2):
─────────────────────────────────────
- "Write clear, well-structured code..."
+ "Write production-quality code that follows
+ industry best practices, including:
+ - Error handling and validation
+ - Comprehensive documentation
+ - Logging for debugging
+ - Unit test coverage"
─────────────────────────────────────

Key Changes:
+ Added: "production-quality code"
+ Added: Specific best practices list
+ Added: Concrete examples
+ Changed: Vague → Specific
```

### 4.3 Score Breakdown

```
Score: 44/50 (88%)
┌─────────────────┬───────┬─────────────────────────────────┐
│ Criterion       │ Score │ Notes                           │
├─────────────────┼───────┼─────────────────────────────────┤
│ Clarity          │ 9/10  | Specific, unambiguous           │
│ Specificity      │ 9/10  | Detailed requirements           │
│ Structure        │ 9/10  | Well-organized sections         │
│ Context          │ 8/10  | Good background info            │
│ Output Format    │ 9/10  | Clear format specified          │
└─────────────────┴───────┴─────────────────────────────────┘
```

---

## Part 5: Persistence Specification

### 5.1 Storage Location

```
~/.dspy_tuning/
├── sessions/
│   ├── session-20260118-143022.json
│   ├── session-20260118-150445.json
│   └── my-improved-prompt.json
├── prompts/
│   ├── my-improved-prompt.toml
│   └── best-practices-guide.toml
└── config.json
```

### 5.2 Session Format (JSON)

```json
{
  "session_id": "session-20260118-143022",
  "created_at": "2026-01-18T14:30:22Z",
  "base_prompt": "Write better code",
  "attempts": [
    {
      "attempt_id": 1,
      "approach": "toml",
      "prompt": "Write clear, well-structured code...",
      "score": 32,
      "score_breakdown": {
        "clarity": 7,
        "specificity": 6,
        "structure": 7,
        "context": 6,
        "output_format": 6
      },
      "timestamp": "2026-01-18T14:30:25Z"
    },
    {
      "attempt_id": 2,
      "approach": "mipro",
      "prompt": "Write production-quality code with...",
      "score": 44,
      "timestamp": "2026-01-18T14:35:10Z"
    }
  ],
  "selected_attempt": 2,
  "selected_approach": "mipro"
}
```

### 5.3 Saved Prompt Format (TOML)

```toml
name = "my-improved-prompt"
created_at = "2026-01-18T14:35:10Z"
approach = "mipro"
score = 44

[prompt]
template = """
Write production-quality code that follows industry best practices:

## Requirements
- Error handling and validation
- Comprehensive documentation
- Logging for debugging
- Unit test coverage

## Output Format
Provide code with inline comments explaining each section.
"""

[metadata]
score_breakdown = { clarity = 9, specificity = 9, structure = 9, context = 8, output_format = 9 }
```

---

## Part 6: Implementation Phases

### Phase 1: Foundation (Days 1-2)
| Task | File | Description |
|------|------|-------------|
| 1.1 | Create `cli.py` | Basic CLI structure with argparse |
| 1.2 | Create `toml.py` | TOML wrapper class |
| 1.3 | Create `improve.py` | ImproveModule |
| 1.4 | Update `modules/__init__.py` | Add improve to registry |

### Phase 2: Framework Consolidation (Days 2-3)
| Task | File | Description |
|------|------|-------------|
| 2.1 | Create `framework/__init__.py` | Framework exports |
| 2.2 | Create `framework/scenarios/improve.py` | ImproveScenario |
| 2.3 | Create `framework/scenarios/architecture.py` | ArchitectureScenario |
| 2.4 | Move `dspy_helm/providers/` | → `framework/providers/` |
| 2.5 | Move `dspy_helm/optimizers/` | → `framework/optimizers/` |
| 2.6 | Move `dspy_helm/evaluation/` | → `framework/evaluation/` |
| 2.7 | Move `dspy_helm/scenarios/` | → `framework/scenarios/` |
| 2.8 | Move `dspy_helm/data/` | → `framework/data/` |
| 2.9 | Move `dspy_helm/config/` | → `framework/config/` |
| 2.10 | Move `dspy_helm/prompts/` | → `framework/prompts/` |

### Phase 3: Interactive Features (Days 3-5)
| Task | File | Description |
|------|------|-------------|
| 3.1 | Update `cli.py` | Add interactive mode |
| 3.2 | Update `cli.py` | Add 5 approaches |
| 3.3 | Update `cli.py` | Add comparison table |
| 3.4 | Update `cli.py` | Add diff view |
| 3.5 | Update `cli.py` | Add persistence |
| 3.6 | Update `cli.py` | Add save/load |
| 3.7 | Update `cli.py` | Add make-module |

### Phase 4: Integration (Days 5-6)
| Task | File | Description |
|------|------|-------------|
| 4.1 | Create `scripts/gemini_dspy_wrapper.py` | Shell-out wrapper |
| 4.2 | Update `GEMINI.md` | Add DSPy commands |
| 4.3 | Create `ARCHITECTURE.md` | Architecture docs |
| 4.4 | Update `meta-dspy.md` | Update references |

### Phase 5: Cleanup (Day 7)
| Task | Description |
|------|-------------|
| 5.1 | Delete `dspy_helm/` directory |
| 5.2 | Delete `dspy_integration/optimizers/` |
| 5.3 | Delete external `/home/masum/github/dspy_integration/` |
| 5.4 | Run full test suite |
| 5.5 | Verify all imports work |

---

## Part 7: Risk Mitigation

### 7.1 High-Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| Consolidation breaks imports | High | Test imports incrementally; keep backups |
| MIPROv2 optimization too slow | Medium | Add timeout, fallback to Bootstrap |
| Persistence format changes | Low | Version field in JSON |
| Gemini CLI shell-out fails | Low | Fallback to direct python call |

### 7.2 Rollback Plan

If issues occur:
```bash
# Restore from backup
git checkout HEAD -- dspy_helm/  # If consolidated

# Revert imports
git checkout HEAD -- dspy_integration/modules/__init__.py

# Remove new files
rm -rf dspy_integration/cli.py
rm -rf dspy_integration/framework/
```

---

## Part 8: Verification Checklist

### 8.1 CLI Commands
```bash
# Terminal
python -m dspy_integration list
python -m dspy_integration improve "test"
python -m dspy_integration compare "test"
python -m dspy_integration interactive  # Check interactive mode works
python -m dspy_integration sessions     # Check persistence works
```

### 8.2 Gemini CLI
```bash
# Inside Gemini CLI
/dspy:improve "test"
/dspy:compare "test"
/dspy:list
/dspy:interactive "test"
```

### 8.3 Imports
```python
# All should work
from dspy_integration import get_module_for_scenario
from dspy_integration.framework import ScenarioRegistry
from dspy_integration.framework.providers import get_provider_by_name
from dspy_integration.framework.optimizers import OptimizerRegistry
```

---

## Part 9: Dependencies

### 9.1 Python Dependencies

```txt
# requirements.txt (existing + new)
dspy-ai>=2.0.0
datasets>=2.0.0
requests>=2.31.0
urllib3>=2.0.0
cloudpickle>=3.0.0
tomli>=2.0.1  # NEW: For TOML parsing (stdlib in Python 3.11+)
```

### 9.2 System Dependencies

```bash
# For persistence
mkdir -p ~/.dspy_tuning/

# For Gemini CLI integration
# (No additional dependencies)
```

---

## Summary

| Aspect | Status |
|--------|--------|
| **Consolidation** | dspy_helm → framework/ |
| **Interactive CLI** | tune/compare/interactive commands |
| **5 Approaches** | TOML, DSPy, MIPROv2, Bootstrap, Custom |
| **Comparison** | Table + diff view |
| **Persistence** | Save to ~/.dspy_tuning/ |
| **Gemini CLI** | Both single-shot + embedded |
| **Total Files Created** | 13 |
| **Total Files Modified** | 4 |
| **Total Files Deleted** | 3 |
| **Estimated Time** | 7 days |
| **Risk Level** | Medium |

---

## Related Documentation

- `IMPLEMENTATION_PLAN.md` - Original prompt systems integration plan
- `DSPY_HELM_IMPLEMENTATION_PLAN.md` - Original dspy-helm framework plan
- `META_TODO.md` - Meta-todo for prompt systems integration
- `ARCHITECTURE.md` - To be created: Final architecture documentation

---

*Document Version: 1.0*  
*Last Updated: January 18, 2026*  
*Status: Ready for Implementation*
