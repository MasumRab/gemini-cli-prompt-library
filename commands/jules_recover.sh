#!/bin/bash
set -euo pipefail

if [ -z "${1:-}" ] || [ -z "${2:-}" ]; then
    echo "Usage: $0 <SESSION_ID> <MESSAGE>"
    exit 1
fi

if [ -z "${JULES_API_KEY:-}" ]; then
    echo "Error: JULES_API_KEY is not set."
    exit 1
fi

if command -v uv &>/dev/null && [ -f "tools/sessions/jules_send_message.py" ]; then
    uv run python -m tools.sessions.jules_send_message "$1" "$2"
elif command -v python3 &>/dev/null && [ -f "tools/sessions/jules_send_message.py" ]; then
    PYTHONPATH=. python3 -m tools.sessions.jules_send_message "$1" "$2"
else
    echo "Warning: Falling back to curl." >&2
    ID="${1#sessions/}"
    curl -sf "https://jules.googleapis.com/v1alpha/sessions/${ID}:sendMessage" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-Goog-Api-Key: ${JULES_API_KEY}" \
        -d "{\"prompt\": \"$2\"}"
fi
