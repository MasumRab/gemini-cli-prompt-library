#!/bin/bash
# Ralph Wiggum Loop Setup Script
# Creates the loop state file and initializes the iterative development process

TASK_PROMPT="$1"
MAX_ITERATIONS="${2:-0}"  # Default to 0 (unlimited) if not provided
COMPLETION_PROMISE="$3"

# Create .gemini directory if it doesn't exist
mkdir -p .gemini

# Create the Ralph loop state file
cat > .gemini/ralph-loop.local.md << EOF
# Ralph Wiggum Loop State

## Task
$TASK_PROMPT

## Configuration
- Max Iterations: ${MAX_ITERATIONS:-unlimited}
- Completion Promise: ${COMPLETION_PROMISE:-NONE_SET}

## Loop Status
- Current Iteration: 1
- Start Time: $(date)
- Status: ACTIVE

## Progress Notes
- Iteration 1 started: $(date)
- Task: $TASK_PROMPT
EOF

echo "Ralph Wiggum loop initialized!"
echo "Task: $TASK_PROMPT"
echo "State file created at: .gemini/ralph-loop.local.md"

if [ "$MAX_ITERATIONS" != "0" ]; then
    echo "Max iterations: $MAX_ITERATIONS"
fi

if [ -n "$COMPLETION_PROMISE" ]; then
    echo "Completion promise: $COMPLETION_PROMISE"
fi

echo ""
echo "Loop is now active. Begin working on the task iteratively."
echo "Check .gemini/ralph-loop.local.md for current status."