# TODO: Phase 2 - Framework Consolidation Tasks
# See: OPTIMAL_CONFIG_PLAN.md Part 6, Phase 2
# These TODOs track progress for consolidating dspy_helm into framework/
#
# IMPORTANT: Before moving files, ensure imports are updated
# Run: grep -r "from dspy_helm" . --include="*.py" to find all references

## Task 2.1: Create framework/__init__.py
# Location: dspy_integration/framework/__init__.py
# Lines: ~80
# Purpose: Framework exports for unified imports
#
# Acceptance Criteria:
# - [ ] from dspy_integration.framework import ScenarioRegistry works
# - [ ] from dspy_integration.framework import OptimizerRegistry works
# - [ ] from dspy_integration.framework import ProviderChain works
# - [ ] from dspy_integration.framework import Evaluator works
#
# Subtasks:
# - [ ] Import all from providers/__init__.py
# - [ ] Import all from optimizers/__init__.py
# - [ ] Import all from scenarios/__init__.py
# - [ ] Import from evaluation/__init__.py
# - [ ] Export in __all__
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 1.1 (Framework Structure)

## Task 2.2: Create framework/scenarios/improve.py - ImproveScenario
# Location: dspy_integration/framework/scenarios/improve.py
# Lines: ~100
# Purpose: Scenario for evaluating improve prompts
#
# Acceptance Criteria:
# - [ ] @ScenarioRegistry.register("improve") works
# - [ ] load_data() returns train/val splits
# - [ ] metric() evaluates prompt quality (0-50 scale)
# - [ ] make_prompt() creates improve prompt from data
#
# Subtasks:
# - [ ] Import BaseScenario from base.py
# - [ ] Define INPUT_FIELDS = ["original_prompt"]
# - [ ] Define OUTPUT_FIELDS = ["improved_prompt", "changes_summary"]
# - [ ] Implement _load_raw_data() from JSONL or inline
# - [ ] Implement metric() with 5 criteria (clarity, specificity, etc.)
# - [ ] Implement make_prompt() template
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 3 (5 Approaches - Evaluation)

## Task 2.3: Create framework/scenarios/architecture.py - ArchitectureScenario
# Location: dspy_integration/framework/scenarios/architecture.py
# Lines: ~120
# Purpose: Scenario for system architecture design
#
# Acceptance Criteria:
# - [ ] @ScenarioRegistry.register("architecture") works
# - [ ] load_data() returns train/val from architecture.jsonl
# - [ ] metric() evaluates architecture quality
# - [ ] make_prompt() creates architecture design prompt
#
# Subtasks:
# - [ ] Create framework/data/architecture.jsonl first
# - [ ] Implement _load_raw_data() to read JSONL
# - [ ] Implement metric() with architecture criteria
# - [ ] Implement make_prompt() with architecture template
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 1.1 (Architecture Scenario)

## Task 2.4-2.10: Move dspy_helm/ to framework/
# IMPORTANT: Do these one at a time, testing after each
#
# Order:
# 1. providers/ (7 files)
# 2. optimizers/ (4 files)
# 3. evaluation/ (2 files)
# 4. scenarios/ (7 files, 2 new)
# 5. data/ (5 JSONL files, 1 new)
# 6. config/ (2 files)
# 7. prompts/ (2 files)
#
# For each directory:
# - [ ] Copy files to framework/<dir>/
# - [ ] Update imports in each file
# - [ ] Test imports work
# - [ ] Delete original dspy_helm/<dir>/
#
# After ALL moves complete:
# - [ ] Delete dspy_helm/ directory
# - [ ] Run: grep -r "from dspy_helm" . --include="*.py" (should be empty)
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 1.1 (Consolidation)

# ============================================================
# QUICK REFERENCE - Phase 2 Tasks Status
# ============================================================
# Task 2.1: framework/__init__.py - [ ] Not Started
# Task 2.2: scenarios/improve.py - [ ] Not Started
# Task 2.3: scenarios/architecture.py - [ ] Not Started
# Task 2.4: Move providers/ - [ ] Not Started
# Task 2.5: Move optimizers/ - [ ] Not Started
# Task 2.6: Move evaluation/ - [ ] Not Started
# Task 2.7: Move scenarios/ - [ ] Not Started
# Task 2.8: Move data/ - [ ] Not Started
# Task 2.9: Move config/ - [ ] Not Started
# Task 2.10: Move prompts/ - [ ] Not Started
#
# Phase 2 Estimated Time: Days 2-3
# ============================================================
