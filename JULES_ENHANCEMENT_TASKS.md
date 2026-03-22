# Jules Tasks: Gemini CLI Enhancement Plan

**Project**: gemini-cli-prompt-library  
**Source**: IMPROVEMENT_PLAN.md  
**Created**: January 18, 2026

---

## Quick Start

Send this file to Jules with:
```
Execute all tasks in this file to implement the Enhancement Plan.
Work through phases 1, 2, 3 sequentially.
Report progress after each phase.
```

---

## Phase 1: Foundational Technical Spike & Dispatcher

**Goal**: Enable natural language to command translation

### Task 1.1: Technical Spike - TUI Capabilities
```bash
# Investigate: Can TUI framework control user input buffer?
# Research: ratatui, textual, rich libraries
# Question to answer: Can we programmatically set cursor position?

# Deliverable: docs/TUI_INPUT_BUFFER_RESEARCH.md
# Answer ONE question: YES or NO?
# - YES: Use "Direct Edit" workflow (Path A)
# - NO: Use "Reference-Based" workflow (Path B)

# Commands to run:
python -c "import ratatui; print('ratatui available')" 2>/dev/null || echo "ratatui not installed"
python -c "import textual; print('textual available')" 2>/dev/null || echo "textual not installed"
```

### Task 1.2: Create Command Manifest
```bash
# Create dspy_integration/framework/manifest.py
# This file will:
# - List all 41 commands from commands/
# - Include metadata: name, category, description, examples
# - Provide lookup by keyword

# Deliverable: dspy_integration/framework/manifest.py
# Test: python -c "from dspy_integration.framework.manifest import get_commands; print(len(get_commands()))"
# Expected: 41 commands
```

### Task 1.3: Build Intelligent Dispatcher
```bash
# Create dspy_integration/framework/dispatcher.py

# The dispatcher takes natural language input and:
# 1. Analyzes the request
# 2. Selects best command from manifest
# 3. Generates refined prompt
# 4. Constructs ready-to-run command

# Example meta-prompt:
"""
You are a command router. User says: "{user_input}"
Available commands:
{command_list}

Select the BEST command and explain why.
Also suggest 2 alternatives.
"""

# Deliverable: dspy_integration/framework/dispatcher.py
# Test: python -c "from dspy_integration.framework.dispatcher import dispatch; print(dispatch('my test is broken'))"
```

### Task 1.4: Implement Core User Workflow

**If Task 1.1 = YES (Path A - Direct Edit)**:
```bash
# Create dspy_integration/ui/input_buffer.py
# - Programmatically set input buffer content
# - Allow user to edit before execution
```

**If Task 1.1 = NO (Path B - Reference-Based)**:
```bash
# Create dspy_integration/cli.py enhancement
# - Output: [1] /workflows:debug-and-fix --error "..."
# - Add: run 1 command to execute reference
```

---

## Phase 2: Unified & Transparent UI

**Goal**: Build Command Recommendation Menu + cass-augmented suggestions

### Task 2.1: Command Recommendation Menu
```bash
# Create dspy_integration/ui/recommendation.py

# Display when /prompts:improve runs:
"""
--- Command Recommendation ---

✅ Based on your request, I recommend:

   /workflows:debug-and-fix --error "login test is failing..."

**Why this choice?**
[Reasoning from dispatcher]

**What would you like to do next?**
1. ▶️ Run Workflow
2. ✍️ Edit Command  
3. 💡 View Alternatives
4. ❌ Cancel
"""

# Deliverable: dspy_integration/ui/recommendation.py
# Test: python -c "from dspy_integration.ui.recommendation import show_recommendation; show_recommendation(...)"
```

### Task 2.2: cass-Augmented Suggestions (Async)
```bash
# Create dspy_integration/search/cass_augmented.py

# When user selects "View Alternatives":
# 1. Background search using cass search patterns
# 2. Pattern 1 (Exact): cass search '"/command" AND "keywords"'
# 3. Pattern 2 (Concept): cass search '"/command" AND (synonyms)'
# 4. Pattern 3 (Fallback): cass search '"/command" AND (passed OR fixed)'

# Deliverable: dspy_integration/search/cass_augmented.py
# Note: Requires cass to be installed (pip install cass)
```

### Task 2.3: Smart Search Layer
```bash
# Create dspy_integration/search/smart_search.py

# Pre-compute search terms from user input:
# - Keywords: "login", "failing", "pointer"
# - Regex: "test_.*login.*\.py"
# - Negative: exclude "javascript" if Python context

# Execute layered search:
# 1. Exact match
# 2. Concept match (with synonyms)
# 3. Command-only fallback

# Deliverable: dspy_integration/search/smart_search.py
```

### Task 2.4: Progression Checklist UI
```bash
# Create dspy_integration/ui/progression.py

# When workflow runs, display:
"""
Workflow: /workflows:debug-and-fix
Status: In Progress...

1. [✓] Confirmed failure by running the test
2. [in_progress] Analyzing user_service.py...
3. [ ] Proposing a code fix
...
"""

# Features:
# - Real-time updates
# - Status indicators (pending, in_progress, completed, failed)
# - Can cancel at any time

# Deliverable: dspy_integration/ui/progression.py
```

---

## Phase 3: Full Agentic Integration

**Goal**: Make "improve" an autonomous agent skill

### Task 3.1: Proactive Workflow Suggestions
```bash
# Create dspy_integration/agents/suggester.py

# When user runs a simple command, agent suggests:
# "I can do that, but I can also use the smart-refactor workflow 
# to automatically verify my changes with tests. Use workflow?"

# Integration: Modify CLI to check if request is workflow candidate

# Deliverable: dspy_integration/agents/suggester.py
# Test: python -c "from dspy_integration.agents.suggester import suggest_workflow; print(suggest_workflow('/code-review:refactor'))"
```

### Task 3.2: Self-Correction Internal Skill
```bash
# Create dspy_integration/agents/self_correct.py

# When workflow step fails:
# 1. Analyze error
# 2. Re-read context
# 3. Rewrite prompt
# 4. Try different approach

# Example:
# - Step fails: tool returns error
# - Call self_correct.analyze(error, context)
# - Get rewritten prompt
# - Retry with new prompt

# Deliverable: dspy_integration/agents/self_correct.py
```

### Task 3.3: Agent Mode CLI Integration
```bash
# Update dspy_integration/cli.py for agent mode

# New commands:
# - /improve --agent "fix my login bug" (auto-suggest)
# - /improve --auto (auto-execute best match)
# - /improve --workflow "multi-step task"

# Add flags:
# --suggest-workflows
# --auto-correct
# --max-retries 3
```

---

## Verification Commands

Run after each phase:

```bash
# Phase 1
python -c "from dspy_integration.framework.manifest import get_commands; print(f'Commands: {len(get_commands)}')"
python -c "from dspy_integration.framework.dispatcher import dispatch; print(dispatch('my test is broken'))"

# Phase 2
python -c "from dspy_integration.ui.recommendation import show_recommendation; print('UI OK')"
python -c "from dspy_integration.search.smart_search import search; print(search('login error'))"

# Phase 3
python -c "from dspy_integration.agents.suggester import suggest_workflow; print(suggest_workflow('refactor'))"
python -c "from dspy_integration.agents.self_correct import SelfCorrect; print('SelfCorrect OK')"
```

---

## Timeline

| Phase | Tasks | Duration |
|-------|-------|----------|
| 1 | 4 tasks | 1-2 days |
| 2 | 4 tasks | 2-3 days |
| 3 | 3 tasks | 1-2 days |
| **Total** | **11 tasks** | **~5 days** |

---

## Send to Jules

Copy this file and send:

```
Execute the Enhancement Plan in this file.

Start with Phase 1, Task 1.1 (TUI capabilities research).
For Task 1.1: Research whether ratatui/textual can control input buffer.
Answer YES or NO - this determines the workflow path.

Then continue with Tasks 1.2, 1.3, 1.4.

Report:
1. Task completed
2. Files created
3. Test output
4. Any blockers

Begin now.
```
