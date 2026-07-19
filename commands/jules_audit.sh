#!/bin/bash
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <SESSION_ID>"
    exit 1
fi

SESSION_ID=$1

if command -v uv &>/dev/null && [ -f "tools/pr/jules_audit_session_pr.py" ]; then
    uv run python -m tools.pr.jules_audit_session_pr "$SESSION_ID"
elif command -v python3 &>/dev/null && [ -f "tools/pr/jules_audit_session_pr.py" ]; then
    PYTHONPATH=. python3 -m tools.pr.jules_audit_session_pr "$SESSION_ID"
else
    echo "Warning: Falling back to curl/bash minimal audit." >&2
    if [ -z "${JULES_API_KEY:-}" ]; then
        echo "Error: JULES_API_KEY is not set. Cannot fetch session info."
        exit 1
    fi
    
    ID="${SESSION_ID#sessions/}"
    SESSION_JSON=$(curl -sf -H "X-Goog-Api-Key: $JULES_API_KEY" "https://jules.googleapis.com/v1alpha/sessions/$ID")
    PR_BRANCH=$(echo "$SESSION_JSON" | jq -r '.outputs[] | select(.pullRequest != null) | .pullRequest.headRef' | head -n 1)
    
    if [ -z "$PR_BRANCH" ] || [ "$PR_BRANCH" == "null" ]; then
        echo "Error: Could not find PR branch for session $SESSION_ID"
        exit 1
    fi
    
    echo "Auditing branch: $PR_BRANCH (minimal check)"
    git fetch origin "$PR_BRANCH"
    
    # Check for build artifacts
    ARTIFACTS=$(git diff "origin/main...origin/$PR_BRANCH" --name-only | grep -E "\.egg-info|/build/|/dist/|__pycache__" || true)
    if [ -n "$ARTIFACTS" ]; then
        echo "❌ FAILED: Build artefacts found:"
        echo "$ARTIFACTS"
        exit 1
    fi
    echo "✅ PASSED: No build artefacts found."
fi
