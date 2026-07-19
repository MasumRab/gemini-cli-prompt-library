#!/bin/bash
# List Jules sessions with optional filtering
# Usage: ./list_sessions.sh [--state STATE] [--page-size N] [--repo REPO] [--dry-run]

set -euo pipefail

DRY_RUN=false
STATE=""
PAGE_SIZE=50
REPO_FILTER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --state) STATE="$2"; shift 2 ;;
        --page-size) PAGE_SIZE="$2"; shift 2 ;;
        --repo) REPO_FILTER="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "=== Jules Session List ==="
[[ "$DRY_RUN" == "true" ]] && echo "*** DRY-RUN MODE - No API calls will be made ***"
echo ""

# Dry-run mode - show mock data
if [[ "$DRY_RUN" == "true" ]]; then
    echo "Session ID | State | Last Activity | Repo"
    echo "-----------|-------|---------------|-----"
    echo "sess_abc123 | COMPLETED | 2026-05-01T14:30Z | <owner>/<repo>"
    echo "sess_def456 | IN_PROGRESS | 2026-05-05T09:15Z | <owner>/<repo>"
    echo "sess_ghi789 | COMPLETED | 2026-04-28T16:45Z | <owner>/<repo>"
    echo ""
    echo "[DRY-RUN] Would fetch real sessions from Jules API"
    echo "[DRY-RUN] Command: curl -f -H \"X-Goog-Api-Key: \$JULES_API_KEY\" -H \"Content-Type: application/json\" https://jules.googleapis.com/v1alpha/sessions?pageSize=$PAGE_SIZE"
    echo ""
    echo "Note: Jules API uses API key header (X-Goog-Api-Key) with API key from Jules Settings"
    echo "Ensure JULES_API_KEY is set in your environment before running"
    exit 0
fi

# Real API call requires token
if [[ -z "${JULES_API_KEY:-}" ]]; then
    echo "Error: JULES_API_KEY not set" >&2
    echo "Ensure JULES_API_KEY is set in your environment before running this script" >&2
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it to run this script." >&2
    exit 1
fi

BASE_URL="https://jules.googleapis.com/v1alpha/sessions"
PARAMS="pageSize=${PAGE_SIZE}"

if [[ -n "$STATE" ]]; then
    PARAMS="${PARAMS}&filter=state%3D%22${STATE}%22"
fi

HEADERS=(-f -H "X-Goog-Api-Key: $JULES_API_KEY" -H "Content-Type: application/json")

echo "Fetching sessions..."
RESPONSE=$(curl -s "${HEADERS[@]}" "$BASE_URL?$PARAMS")

if [[ -z "$RESPONSE" ]]; then
    echo "No sessions found or API error"
    exit 1
fi

echo "$RESPONSE" | jq -r '.sessions[]? | "\(.name // "N/A") | \(.state // "UNKNOWN") | \(.lastActivityTime // "N/A") | \(.displayName // "No name")"' || echo "Error parsing response (install jq for better output)"
