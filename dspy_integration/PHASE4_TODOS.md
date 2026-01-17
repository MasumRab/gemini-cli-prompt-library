# TODO: Phase 4 - Integration Tasks
# See: OPTIMAL_CONFIG_PLAN.md Part 6, Phase 4
# These TODOs track progress for integration work

## Task 4.1: Create scripts/gemini_dspy_wrapper.py
# Location: scripts/gemini_dspy_wrapper.py
# Lines: ~80
# Purpose: Shell-out wrapper for Gemini CLI integration
#
# Acceptance Criteria:
# - [ ] Can be called from Gemini CLI
# - [ ] Accepts JSON input from stdin
# - [ ] Returns JSON output to stdout
# - [ ] Handles errors gracefully
# - [ ] Supports all dspy: commands
#
# Subtasks:
# - [ ] Create main() function
# - [ ] Parse JSON from stdin
# - [ ] Call appropriate CLI function
# - [ ] Format result as JSON
# - [ ] Handle errors with JSON error messages
# - [ ] Test with simple command
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 2.3 (Gemini CLI Commands)

## Task 4.2: Update GEMINI.md - Add DSPy Commands
# Location: GEMINI.md
# Changes: Add /dspy:* commands documentation
#
# Acceptance Criteria:
# - [ ] /dspy:improve documented
# - [ ] /dspy:evaluate documented
# - [ ] /dspy:compare documented
# - [ ] /dspy:optimize documented
# - [ ] /dspy:interactive documented
# - [ ] /dspy:list documented
# - [ ] /dspy:sessions documented
# - [ ] Examples for each command
#
# Subtasks:
# - [ ] Create "DSPy Commands" section
# - [ ] Document each /dspy:* command
# - [ ] Add examples
# - [ ] Add notes about --optimizer flags
# - [ ] Add notes about --parallel flag
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 2.3 (Gemini CLI Commands)

## Task 4.3: Create ARCHITECTURE.md
# Location: ARCHITECTURE.md
# Lines: ~200
# Purpose: Architecture documentation for the unified system
#
# Acceptance Criteria:
# - [ ] Directory structure documented
# - [ ] Module relationships explained
# - [ ] Data flow documented
# - [ ] Import paths documented
# - [ ] CLI usage documented
# - [ ] Gemini CLI integration documented
#
# Subtasks:
# - [ ] Document new directory structure
# - [ ] Explain framework/ vs modules/
# - [ ] Show data flow diagrams
# - [ ] Document import paths
# - [ ] Document CLI commands
# - [ ] Document Gemini CLI integration
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 1.1 (Directory Structure)

## Task 4.4: Update meta-dspy.md
# Location: meta-dspy.md
# Changes: Update with new architecture, remove dspy_helm references
#
# Acceptance Criteria:
# - [ ] dspy_helm references removed or updated
# - [ ] framework/ structure documented
# - [ ] CLI usage examples updated
# - [ ] DSPy module examples updated
#
# Subtasks:
# - [ ] Find all dspy_helm references
# - [ ] Update or remove each
# - [ ] Add framework/ documentation
# - [ ] Update CLI examples
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 1.3 (Files to Modify)

# ============================================================
# QUICK REFERENCE - Phase 4 Tasks Status
# ============================================================
# Task 4.1: gemini_dspy_wrapper.py - [ ] Not Started
# Task 4.2: GEMINI.md update - [ ] Not Started
# Task 4.3: ARCHITECTURE.md - [ ] Not Started
# Task 4.4: meta-dspy.md update - [ ] Not Started
#
# Phase 4 Estimated Time: Days 5-6
# ============================================================

## Pre-Integration Checklist
# Before Phase 4, complete:
# - [ ] Phase 1 complete (all 4 tasks)
# - [ ] Phase 2 complete (all 10 tasks)
# - [ ] Phase 3 complete (all 6 tasks)
# - [ ] All imports working
# - [ ] All tests passing
# - [ ] CLI commands tested
