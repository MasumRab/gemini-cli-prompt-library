#!/bin/bash
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <PR_NUMBER_OR_BRANCH>"
    exit 1
fi

if command -v uv &>/dev/null && [ -f "tools/pr/jules_pr_context.py" ]; then
    uv run python -m tools.pr.jules_pr_context "$@"
elif command -v python3 &>/dev/null && [ -f "tools/pr/jules_pr_context.py" ]; then
    PYTHONPATH=. python3 -m tools.pr.jules_pr_context "$@"
else
    # Fallback using pure gh CLI if Python script isn't available
    echo "Warning: Falling back to native gh CLI." >&2
    echo "PR: $1"
    echo "--- Metrics & Status ---"
    gh pr view "$1"
    echo "--- Checks ---"
    gh pr checks "$1"
    echo "--- Comments ---"
    gh pr view "$1" --comments
fi
