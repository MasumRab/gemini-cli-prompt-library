#!/bin/bash
set -e
# Naming Convention: jules_triage
# Unified entry point for Jules triage and recovery.

# Standardize on JULES_API_KEY
export JULES_API_KEY="${JULES_API_KEY}"

if [ -z "$JULES_API_KEY" ]; then
    echo "ERROR: JULES_API_KEY not set." >&2
    exit 1
fi

# Primary: Python client (robust pagination + A+ grading)
if [ -f "tools/sessions/jules_list_sessions.py" ]; then
    uv run python3 -m tools.sessions.jules_list_sessions "$@"
else
    # Fallback: curl
    echo "Warning: Falling back to curl." >&2
    curl -sf 'https://jules.googleapis.com/v1alpha/sessions?pageSize=20' \
        -H "X-Goog-Api-Key: $JULES_API_KEY"
fi
