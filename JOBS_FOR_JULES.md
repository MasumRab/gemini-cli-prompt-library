# Jules Jobs - Complete Project Execution

**Project**: gemini-cli-prompt-library  
**Created**: January 18, 2026  
**Purpose**: Execute all project phases via Jules AI agent sessions

---

## Quick Start

Send this entire file to Jules with the prompt:
```
Execute all tasks in this file. Start with Phase 2, Task 2.1.1 and work through sequentially.
Report progress after each task. If a task is blocked, explain why.
```

---

## Phase 2: Framework Consolidation + Dispatcher

**Duration**: 2-3 days  
**Dependency**: None (start here)

### Track A: Framework Structure

#### Task 2.1.1: Create framework/__init__.py
```bash
Create dspy_integration/framework/__init__.py with exports:
- from .registry import CommandRegistry, get_command
- from .dispatcher import IntelligentDispatcher
- from .providers import get_provider
- from .optimizers import get_optimizer
- from .evaluation import Evaluator
```
**Verify**: `python -c "from dspy_integration.framework import CommandRegistry; print('OK')"`

#### Task 2.1.2: Create framework/providers/
```bash
Create dspy_integration/framework/providers/__init__.py
Copy files from dspy_helm/providers/:
- base.py, gemini.py, groq.py, huggingface.py
- openrouter.py, opencode.py, opencode_zen.py, qwen.py, puter.py
```

#### Task 2.1.3: Create framework/optimizers/
```bash
Create dspy_integration/framework/optimizers/__init__.py
Copy from dspy_helm/optimizers/:
- base.py, mipro_v2.py, bootstrap.py
```

#### Task 2.1.4: Create framework/evaluation/
```bash
Create dspy_integration/framework/evaluation/__init__.py
Copy from dspy_helm/eval/evaluate.py
```

---

### Track B: Dispatcher Components

#### Task 2.2.1: Create framework/registry.py
```bash
Create dspy_integration/framework/registry.py with:
- CommandRegistry class that auto-discovers 41 commands from commands/
- Loads metadata from TOML files
- Provides search() by keyword
- Provides list_by_category()
- Provides get_command()
```
**Test**: Create tests/test_registry.py with 4 tests

#### Task 2.2.2: Create framework/dispatcher.py
```bash
Create dspy_integration/framework/dispatcher.py with:
- IntelligentDispatcher class
- dispatch(user_request) → command match
- _keyword_match() for basic selection
- _refine_prompt() for prompt optimization
- _find_alternatives() for alternatives
```
**Test**: Create tests/test_dispatcher.py with 5 tests

#### Task 2.2.3: Add CLI dispatcher integration
```bash
In dspy_integration/cli.py:
- Add `dispatch` command
- Add `improve --smart` flag that uses dispatcher
- Update `improve` to show alternatives
```

---

### Track C: CLI Improvements

#### Task 2.3.1: Add forgiving CLI parsing
```bash
In dspy_integration/cli.py:
- Add normalize_args() function
- Single-dash to double-dash conversion
- Flag typo correction (edit distance <= 2)
- Command alias resolution (find→search, ls→stats)
```

#### Task 2.3.2: Add robot mode
```bash
Add robot/AI mode flags in cli.py:
- --robot: Enable robot mode
- --robot-format: json, jsonl, compact
- --robot-meta: Include performance metadata
- --fields: Comma-separated fields
- --max-content-length: Truncation
- --max-tokens: Soft budget
```

#### Task 2.3.3: Complete unimplemented CLI methods
```bash
Complete these methods in DSPyIntegrationCLI:
- interactive() [currently placeholder]
- sessions() [currently placeholder]
- optimize() [currently returns placeholder]
```

---

### Track D: Consolidation

#### Task 2.4.1-2.4.5: Move dspy_helm to framework
```bash
git mv dspy_helm/providers framework/
git mv dspy_helm/optimizers framework/
git mv dspy_helm/evaluation framework/
git mv dspy_helm/scenarios framework/
git mv dspy_helm/data framework/
```

#### Task 2.4.6: Update imports
```bash
Update imports in:
- dspy_helm/__init__.py
- dspy_helm/cli.py
- tests/*.py
- scripts/*.py
```

---

## Phase 3: UI + CASS Integration

**Duration**: 3-4 days  
**Dependency**: Phase 2 Complete

### Track A: UI Components

#### Task 3.1.1: Design Menu UI spec
```bash
Create docs/MENU_UI_SPEC.md with:
- Layout design (recommendation panel)
- Color scheme (success/warning/info)
- Keyboard shortcuts
- Interaction flows
- Mockup examples
```

#### Task 3.1.2: Create ui/menu.py
```bash
Create dspy_integration/ui/menu.py with MenuRenderer class:
- render_recommendation(command, alternatives)
- render_alternatives(results)
- render_checklist(progress)
- format_with_highlight(text)
```

#### Task 3.1.3: Create ui/recommendation.py
```bash
Create dspy_integration/ui/recommendation.py:
- RecommendationPanel class
- CassAugmentedSuggestions (async search)
- Display historical examples
```

#### Task 3.1.4: Create ui/progression.py
```bash
Create dspy_integration/ui/progression.py:
- ProgressionChecklist class
- start_workflow(), update_step(), display(), complete()
```

---

### Track B: CASS Integration

#### Task 3.2.1: Create semantic/hash_embedder.py
```bash
Create dspy_integration/semantic/hash_embedder.py:
- HashEmbedder class (FNV-1a)
- __init__() → instant (<1ms)
- embed(text) → vector[384]
- No ML dependencies
```

#### Task 3.2.2: Create semantic/edge_ngram.py
```bash
Create dspy_integration/semantic/edge_ngram.py:
- EdgeNGramIndexer class
- add_document(), build_index(), search()
- O(1) prefix matching
```

#### Task 3.2.3: Create semantic/vector_index.py
```bash
Create dspy_integration/semantic/vector_index.py:
- VectorIndex class (CVVI format)
- Memory-mapped loading
- save(), load(), add(), search()
```

#### Task 3.2.4: Integrate cass-style search
```bash
In dspy_integration/:
- create_search_index(commands_dir)
- semantic_search(query) → HashEmbedder
- lexical_search(query) → EdgeNGram
- hybrid_search(query) → RRF combination
```

---

### Track C: 5 Approaches

#### Task 3.3.1: Implement MIPROv2 approach
```bash
In dspy_integration/approaches/:
- approach_mipro(prompt, trainset, valset)
- MIPROv2 optimizer configuration
```
**Test**: test_mipro_approach.py

#### Task 3.3.2: Implement Bootstrap approach
```bash
In dspy_integration/approaches/:
- approach_bootstrap(prompt)
- BootstrapFewShotWithRandomSearch
```
**Test**: test_bootstrap_approach.py

#### Task 3.3.3: Implement Custom approach
```bash
In dspy_integration/approaches/:
- approach_custom(prompt, focus, examples)
- Focus: clarity, specificity, structure, context, output
```

#### Task 3.3.4: Add approach selection UI
```bash
In cli.py:
- --approach flag (toml, dspy, mipro, bootstrap, custom)
- --focus flag (for custom)
- --examples flag (for custom)
- Display approach comparison table
```

---

### Track D: Interactive Mode

#### Task 3.4.1: Create interactive/session.py
```bash
Create dspy_integration/interactive/session.py:
- InteractiveSession class
- add_attempt(), set_selected(), save(), load()
```

#### Task 3.4.2: Create interactive/history.py
```bash
Create dspy_integration/interactive/history.py:
- SessionHistory class
- list_sessions(), load_session(), delete_session()
- Storage: ~/.dspy_tuning/sessions/
```

#### Task 3.4.3: Create interactive/completer.py
```bash
Create dspy_integration/interactive/completer.py:
- CommandCompleter class
- complete_command(), complete_approach(), complete_filename()
- For readline integration
```

#### Task 3.4.4: Full REPL implementation
```bash
Create dspy_integration/interactive/repl.py:
- main() → run_repl()
- Commands: try, compare, diff, pick, save, load, sessions, help, quit
- Readline: history, tab completion, vi mode
```

---

## Phase 4: Agentic Integration

**Duration**: 2-3 days  
**Dependency**: Phase 3 Complete

### Track A: Proactive Suggestions

#### Task 4.1.1: Create agents/suggester.py
```bash
Create dspy_integration/agents/suggester.py:
- WorkflowSuggester class
- analyze_request() → is_workflow_candidate()
- get_suggestion() → Suggestion
```

#### Task 4.1.2: Add workflow detection logic
```bash
Create dspy_integration/agents/detection.py:
- detect_workflow_type()
- detect_implied_steps()
- estimate_complexity()
- detect_context_requirements()
```

#### Task 4.1.3: Create suggestion UI
```bash
Create dspy_integration/ui/suggestion.py:
- SuggestionDisplay class
- show_suggestion(), format_workflow_steps()
```

#### Task 4.1.4: Integrate with CLI
```bash
In cli.py:
- Add --auto-suggest flag
- Add --auto-accept flag
- Modify improve command to check suggestions
```

---

### Track B: Self-Correction Skills

#### Task 4.2.1: Create agents/self_correct.py
```bash
Create dspy_integration/agents/self_correct.py:
- SelfCorrectSkill class
- analyze_failure(), rewrite_prompt()
- should_retry(), get_retry_strategy()
```

#### Task 4.2.2: Add error analysis logic
```bash
Create dspy_integration/agents/error_analyzer.py:
- categorize_error()
- extract_error_pattern()
- find_similar_issues()
- generate_fix_suggestion()
```

#### Task 4.2.3: Add prompt rewriting
```bash
Create dspy_integration/agents/prompt_rewriter.py:
- rewrite_with_context()
- add_constraints(), simplify_prompt(), expand_prompt()
```

#### Task 4.2.4: Add retry mechanism
```bash
Create dspy_integration/agents/retry_manager.py:
- RetryManager class
- execute_with_retry()
- on_failure(), track_attempts()
- Exponential backoff
```

---

### Track C: Integration

#### Task 4.3.1: Update CLI for agent mode
```bash
In cli.py:
- Add --agent-mode flag
- Add --auto-correct flag
- Add --max-retries flag
```

#### Task 4.3.2: Add agent config
```bash
Create dspy_integration/config/agent.yaml:
```yaml
agent:
  auto_suggest: true
  auto_correct: true
  max_retries: 3
  suggestion_threshold: 0.7
```

#### Task 4.3.3: Create agent docs
```bash
Create docs/AGENT_MODE.md:
- How agent mode works
- Configuration options
- Examples
- Troubleshooting
```

---

## Phase 5: Cleanup & Release

**Duration**: 1 day  
**Dependency**: All Phases Complete

### Task 5.1: Directory Cleanup
```bash
rm -rf dspy_helm/
rm -rf dspy_integration/optimizers/
```

### Task 5.2: Run Test Suite
```bash
pytest tests/ -v --tb=short
# Fix any failures
# Target: 80% coverage
```

### Task 5.3: Verify All Imports
```bash
python -c "
from dspy_integration import get_module_for_scenario
from dspy_integration.framework import CommandRegistry
from dspy_integration.framework import IntelligentDispatcher
print('All imports work!')
"
```

### Task 5.4: Verify CLI Commands
```bash
python -m dspy_integration --help
python -m dspy_integration list
python -m dspy_integration improve "test"
python -m dspy_integration dispatch "fix login bug"
python -m dspy_integration --robot --json list
```

### Task 5.5: Create pyproject.toml
```bash
Create pyproject.toml with:
- name, version, description
- requires-python >=3.11
- dependencies
- entry points
```

### Task 5.6: Update CHANGELOG.md
```bash
Document all changes in CHANGELOG.md:
- New features
- Breaking changes
- Bug fixes
```

---

## Verification Checklist

Run after each phase:

```bash
# Phase 2
python -c "from dspy_integration.framework import CommandRegistry; print('Registry OK')"
python -c "from dspy_integration.framework import IntelligentDispatcher; print('Dispatcher OK')"

# Phase 3
python -m dspy_integration list
python -m dspy_integration improve "test" --approach dspy
python -m dspy_integration --robot --json list

# Phase 4
python -m dspy_integration improve "fix bug" --agent-mode --help

# Phase 5
pytest tests/ -v --tb=short
```

---

## Estimated Timeline

| Phase | Tasks | Parallel Tracks | Duration |
|-------|-------|-----------------|----------|
| 2 | 14 | 4 | 2-3 days |
| 3 | 15 | 4 | 3-4 days |
| 4 | 9 | 3 | 2-3 days |
| 5 | 6 | 1 | 1 day |
| **Total** | **44** | - | **~8-10 days** |

---

## Send to Jules

Copy this entire file and send to Jules with:

```
Execute all tasks in this file. 
Start with Phase 2, Task 2.1.1 (Create framework/__init__.py).
Work through tasks in order within each phase.
Report:
1. Task completed
2. Any errors encountered
3. Files created/modified
4. Verification command output

Begin now.
```
