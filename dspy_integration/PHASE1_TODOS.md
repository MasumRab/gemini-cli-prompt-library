# TODO: Phase 1 - Foundation Tasks
# See: OPTIMAL_CONFIG_PLAN.md Part 6, Phase 1
# These TODOs track progress for initial foundation work

## Task 1.1: Create cli.py - Basic CLI Structure
# Location: dspy_integration/cli.py
# Lines: ~400
# Purpose: Unified CLI entry point with all commands
#
# Acceptance Criteria:
# - [ ] argparse.ArgumentParser setup works
# - [ ] 'improve' subcommand exists and returns output
# - [ ] 'evaluate' subcommand exists and returns score
# - [ ] 'list' subcommand exists and lists scenarios
# - [ ] 'interactive' subcommand exists and enters loop
# - [ ] Help text displays all available commands
#
# Subtasks:
# - [ ] Create main() function with argument parsing
# - [ ] Implement improve() function
# - [ ] Implement evaluate() function
# - [ ] Implement list() function
# - [ ] Implement convert() function
# - [ ] Add --output-format argument (json/text)
# - [ ] Add --provider argument
# - [ ] Add error handling
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 2 (CLI Commands Specification)

## Task 1.2: Create toml.py - TOML Wrapper
# Location: dspy_integration/toml.py
# Lines: ~150
# Purpose: TOML wrapper with DSPy fallback for Approach 1
#
# Acceptance Criteria:
# - [ ] load_prompt("improve") returns TOMLPrompt object
# - [ ] TOMLPrompt.execute(prompt) returns improved prompt string
# - [ ] Variables extracted correctly ({{args}}, {{code}}, etc.)
# - [ ] Fallback to DSPy works if TOML fails
#
# Subtasks:
# - [ ] Create TOMLPrompt class
# - [ ] Create TOMLManager class
# - [ ] Implement _extract_variables() regex
# - [ ] Implement execute() with variable substitution
# - [ ] Create fallback_to_dspy() method
# - [ ] Add error handling for missing files
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 3 (Approach 1: TOML-based)

## Task 1.3: Create improve.py - ImproveModule
# Location: dspy_integration/modules/improve.py
# Lines: ~60
# Purpose: DSPy module for prompt improvement (Approach 2)
#
# Acceptance Criteria:
# - [ ] ImproveSignature class exists with correct fields
# - [ ] ImproveModule class exists with ChainOfThought
# - [ ] forward() returns improved_prompt and changes_summary
# - [ ] Compatible with get_module_for_scenario("improve")
#
# Subtasks:
# - [ ] Define ImproveSignature with InputField/OutputField
# - [ ] Create ImproveModule class
# - [ ] Implement forward() method
# - [ ] Add docstrings
# - [ ] Add type hints
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 3 (Approach 2: DSPy Basic)

## Task 1.4: Update modules/__init__.py - Add improve
# Location: dspy_integration/modules/__init__.py
# Changes: Add "improve" to _SCENARIOS_TO_MODULES
#
# Acceptance Criteria:
# - [ ] get_module_for_scenario("improve") returns Improve class
# - [ ] get_optimizer_for_scenario("improve") returns ImproveOptimizer class
# - [ ] No import errors
#
# Subtasks:
# - [ ] Add "improve" to conditional imports (if False: block)
# - [ ] Add "improve" to _SCENARIOS_TO_MODULES dict
# - [ ] Add improve imports to imports dict
# - [ ] Test get_module_for_scenario("improve")
# - [ ] Test get_optimizer_for_scenario("improve")
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 1.2 (Files to Modify)

# ============================================================
# QUICK REFERENCE - Phase 1 Tasks Status
# ============================================================
# Task 1.1: cli.py - [ ] Not Started
# Task 1.2: toml.py - [ ] Not Started
# Task 1.3: improve.py - [ ] Not Started
# Task 1.4: modules/__init__.py - [ ] Not Started
#
# Phase 1 Estimated Time: Days 1-2
# ============================================================
