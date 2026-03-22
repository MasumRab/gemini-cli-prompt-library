# TODO: Phase 3 - Interactive Features Tasks
# See: OPTIMAL_CONFIG_PLAN.md Part 6, Phase 3
# These TODOs track progress for interactive tuning workflow
#
# This phase adds the core interactive capabilities:
# - Interactive session mode
# - 5 Approaches implementation
# - Comparison table view
# - Diff view
# - Persistence
# - Save/Load functionality

## Task 3.1: Update cli.py - Add Interactive Mode
# Location: dspy_integration/cli.py (from Task 1.1)
# Changes: Add interactive() function and command
#
# Acceptance Criteria:
# - [ ] 'interactive' command enters session loop
# - [ ] 'try' command works with all 5 approaches
# - [ ] 'compare' command displays table
# - [ ] 'diff' command shows changes
# - [ ] 'pick' command selects best version
# - [ ] 'save' command persists session
# - [ ] 'load' command restores session
# - [ ] 'quit' command exits with save prompt
#
# Subtasks:
# - [ ] Implement interactive_session() function
# - [ ] Create command parser for session
# - [ ] Add try_handler() for all approaches
# - [ ] Add compare_handler() for table view
# - [ ] Add diff_handler() for changes
# - [ ] Add pick_handler() for selection
# - [ ] Add save_handler() for persistence
# - [ ] Add load_handler() for restoration
# - [ ] Add quit_handler() with save prompt
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 2.2 (Interactive Session)

## Task 3.2: Update cli.py - Implement 5 Approaches
# Location: dspy_integration/cli.py
# Changes: Add all 5 approach implementations
#
# Acceptance Criteria:
# - [ ] approach_toml() - Uses TOML improve.toml
# - [ ] approach_dspy() - Uses ImproveModule
# - [ ] approach_mipro() - Runs MIPROv2 optimization
# - [ ] approach_bootstrap() - Runs BootstrapFewShot
# - [ ] approach_custom() - Targeted refinement with --focus
#
# Approach Details (from OPTIMAL_CONFIG_PLAN.md Part 3):
# 1. TOML-based: Load commands/prompts/improve.toml, execute
# 2. DSPy Basic: Use ImproveModule with ChainOfThought
# 3. MIPROv2: Run full optimization pipeline
# 4. Bootstrap: Run BootstrapFewShot optimization
# 5. Custom: Refine with focus areas (clarity, specificity, etc.)
#
# Subtasks:
# - [ ] Implement approach_toml(prompt)
# - [ ] Implement approach_dspy(prompt)
# - [ ] Implement approach_mipro(prompt) - requires trainset
# - [ ] Implement approach_bootstrap(prompt) - requires trainset
# - [ ] Implement approach_custom(prompt, focus, examples)
# - [ ] Add timeout handling for slow approaches
# - [ ] Add error handling for each approach
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 3 (5 Approaches Specification)

## Task 3.3: Update cli.py - Add Comparison Table
# Location: dspy_integration/cli.py
# Changes: Add comparison table display
#
# Acceptance Criteria:
# - [ ] Table format matches OPTIMAL_CONFIG_PLAN.md Part 4
# - [ ] Columns: #, Approach, Result, Score
# - [ ] Sorting by score (descending)
# - [ ] Color coding for scores (green/yellow/red)
#
# Subtasks:
# - [ ] Create format_comparison_table() function
# - [ ] Add score sorting
# - [ ] Add color codes (ANSI)
# - [ ] Handle long results (truncate)
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 4.1 (Table View)

## Task 3.4: Update cli.py - Add Diff View
# Location: dspy_integration/cli.py
# Changes: Add diff between two attempts
#
# Acceptance Criteria:
# - [ ] Shows additions (green with +)
# - [ ] Shows deletions (red with -)
# - [ ] Shows key changes summary
# - [ ] Works with any two attempt numbers
#
# Subtasks:
# - [ ] Implement diff_attempts(attempt1, attempt2)
# - [ ] Use difflib for comparison
# - [ ] Format as unified diff
# - [ ] Extract key changes summary
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 4.2 (Diff View)

## Task 3.5: Update cli.py - Add Persistence
# Location: dspy_integration/cli.py
# Changes: Add save/load sessions to ~/.dspy_tuning/
#
# Acceptance Criteria:
# - [ ] ~/.dspy_tuning/sessions/ directory created
# - [ ] Session saved as JSON with all attempts
# - [ ] Session loaded from JSON
# - [ ] sessions command lists all saved
# - [ ] delete command removes saved session
# - [ ] Version field in JSON for future compatibility
#
# Persistence Format (from OPTIMAL_CONFIG_PLAN.md Part 5):
# {
#   "session_id": "...",
#   "created_at": "...",
#   "base_prompt": "...",
#   "attempts": [...],
#   "selected_attempt": N,
#   "selected_approach": "..."
# }
#
# Subtasks:
# - [ ] Create persist_session() function
# - [ ] Create load_session() function
# - [ ] Create list_sessions() function
# - [ ] Create delete_session() function
# - [ ] Handle directory creation
# - [ ] Handle file read/write errors
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 5 (Persistence)

## Task 3.6: Update cli.py - Add make-module
# Location: dspy_integration/cli.py
# Changes: Convert selected attempt to DSPy module
#
# Acceptance Criteria:
# - [ ] Takes selected prompt
# - [ ] Generates DSPy module code
# - [ ] Saves to file
# - [ ] Returns module code
#
# Subtasks:
# - [ ] Implement generate_module_code(prompt)
# - [ ] Create module template
# - [ ] Add Signature definition
# - [ ] Add Module class with ChainOfThought
# - [ ] Save to file or print
#
# Related: OPTIMAL_CONFIG_PLAN.md Part 2.2 (make-module command)

# ============================================================
# QUICK REFERENCE - Phase 3 Tasks Status
# ============================================================
# Task 3.1: cli.py interactive mode - [ ] Not Started
# Task 3.2: 5 approaches - [ ] Not Started
# Task 3.3: Comparison table - [ ] Not Started
# Task 3.4: Diff view - [ ] Not Started
# Task 3.5: Persistence - [ ] Not Started
# Task 3.6: make-module - [ ] Not Started
#
# Phase 3 Estimated Time: Days 3-5
# ============================================================
