#!/bin/bash
# Jules Commands for gemini-cli-prompt-library
# Usage: bash jules_commands.sh

# Note: Before running, install Jules:
# curl -fsSL "https://raw.githubusercontent.com/GoogleChromeLabs/Jules/main/install.sh" | bash

REPO="MasumRab/gemini-cli-prompt-library"
SESSION_FILE="JULES_ENHANCEMENT_TASKS.md"

echo "============================================="
echo "Jules Commands for Enhancement Plan"
echo "============================================="
echo ""
echo "Repository: $REPO"
echo "Tasks File: $SESSION_FILE"
echo ""

# Option 1: Read from file and send
echo "Option 1: Send Enhancement Plan (11 tasks, ~5 days)"
echo "-------------------------------------------"
echo "jules remote new --repo $REPO --session \"\$(cat $SESSION_FILE)\""
echo ""

# Option 2: Direct command
echo "Option 2: Direct command"
echo "-------------------------------------------"
cat << 'EOF'
jules remote new --repo MasumRab/gemini-cli-prompt-library --session "
Execute the Enhancement Plan in JULES_ENHANCEMENT_TASKS.md.

Start with Phase 1, Task 1.1:
- Research if TUI framework (ratatui/textual) can control input buffer
- Answer YES or NO - this determines workflow path
- Create docs/TUI_INPUT_BUFFER_RESEARCH.md

Then continue with:
- Task 1.2: Create command manifest (41 commands)
- Task 1.3: Build intelligent dispatcher
- Task 1.4: Implement core workflow

Report after each task with:
1. Task completed
2. Files created/modified
3. Test output
4. Any blockers

Begin now.
"
EOF
echo ""

# Option 3: Enhancement Plan only (11 tasks)
echo "Option 3: Full Enhancement Plan (copy-paste)"
echo "-------------------------------------------"
echo "jules remote new --repo MasumRab/gemini-cli-prompt-library --session \"\$(cat JULES_ENHANCEMENT_TASKS.md)\""
echo ""

# Option 4: Full Project (44 tasks)
echo "Option 4: Full Project (copy-paste)"
echo "-------------------------------------------"
echo "jules remote new --repo MasumRab/gemini-cli-prompt-library --session \"\$(cat JOBS_FOR_JULES.md)\""
echo ""

# Check status
echo "============================================="
echo "Check Jules Status"
echo "============================================="
echo ""
echo "# List all sessions"
echo "jules remote list --session"
echo ""
echo "# Pull results"
echo "jules remote pull --session <SESSION_ID>"
echo ""

# Create session content file
echo "============================================="
echo "Creating session content file..."
echo "============================================="

cat > /tmp/jules_session.txt << 'SESSIONEOF'
Execute the Enhancement Plan in JULES_ENHANCEMENT_TASKS.md.

START WITH PHASE 1, TASK 1.1:
1. Research if TUI framework (ratatui/textual) can programmatically control user input buffer
2. Answer YES or NO in docs/TUI_INPUT_BUFFER_RESEARCH.md
   - YES = use "Direct Edit" workflow (Path A)
   - NO = use "Reference-Based" workflow (Path B)

THEN CONTINUE:
- Task 1.2: Create dspy_integration/framework/manifest.py (41 commands)
- Task 1.3: Build dspy_integration/framework/dispatcher.py
- Task 1.4: Implement core workflow

AFTER PHASE 1 COMPLETE:
- Task 2.1: Create Command Recommendation Menu
- Task 2.2: cass-Augmented Suggestions
- Task 2.3: Smart Search Layer
- Task 2.4: Progression Checklist UI

AFTER PHASE 2 COMPLETE:
- Task 3.1: Proactive Workflow Suggestions
- Task 3.2: Self-Correction Internal Skill
- Task 3.3: Agent Mode CLI Integration

AFTER ALL PHASES:
- Run verification commands
- Report completion

SESSIONEOF

echo "Created: /tmp/jules_session.txt"
echo ""

echo "============================================="
echo "Quick Copy-Paste for Jules"
echo "============================================="
echo ""
echo "# Copy this and run in terminal:"
echo ""
cat /tmp/jules_session.txt | tr '\n' ' ' | sed 's/  */ /g' | xargs -0 echo "jules remote new --repo MasumRab/gemini-cli-prompt-library --session"
echo ""
