#!/bin/bash
# Sync session data from Jules API to local JSON files
# Usage:
#   ./sync_session.sh SESSION_ID [PR_NUMBER]
#   ./sync_session.sh 15863163327149061241 571
#
# Requires: JULES_API_KEY environment variable

set -e

SESSION_ID="${1:?Usage: $0 SESSION_ID [PR_NUMBER]}"
PR_NUMBER="${2:-$(date +%s)}"

OUTPUT_DIR="${JULES_SESSIONS_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)/jules_sessions}"
mkdir -p "$OUTPUT_DIR"

if [[ -z "$JULES_API_KEY" ]]; then
    echo "Error: JULES_API_KEY not set"
    echo "Get your API key from Google AI Studio: https://aistudio.google.com/apikey"
    exit 1
fi

echo "=== Syncing Session $SESSION_ID ==="

# Fetch session metadata
echo "Fetching session metadata..."
curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID" \
    -H "x-goog-api-key: $JULES_API_KEY" \
    > "$OUTPUT_DIR/pr${PR_NUMBER}_session.json"

# Check for error
if jq -e '.error' "$OUTPUT_DIR/pr${PR_NUMBER}_session.json" > /dev/null 2>&1; then
    echo "Error fetching session:"
    jq -r '.error.message // .error' "$OUTPUT_DIR/pr${PR_NUMBER}_session.json"
    rm "$OUTPUT_DIR/pr${PR_NUMBER}_session.json"
    exit 1
fi

# Fetch activities
echo "Fetching session activities..."
curl -s "https://jules.googleapis.com/v1alpha/sessions/$SESSION_ID/activities" \
    -H "x-goog-api-key: $JULES_API_KEY" \
    > "$OUTPUT_DIR/pr${PR_NUMBER}_activities.json"

# Summary
echo ""
echo "=== Session Synced ==="
echo "Session: $SESSION_ID"
echo "PR: #$PR_NUMBER"
echo "Files:"
echo "  - $OUTPUT_DIR/pr${PR_NUMBER}_session.json"
echo "  - $OUTPUT_DIR/pr${PR_NUMBER}_activities.json"
echo ""
echo "State: $(jq -r '.state' "$OUTPUT_DIR/pr${PR_NUMBER}_session.json")"
echo "Title: $(jq -r '.title' "$OUTPUT_DIR/pr${PR_NUMBER}_session.json")"

# Check for PR
PR_URL=$(jq -r '.outputs[]?.pullRequest?.url // empty' "$OUTPUT_DIR/pr${PR_NUMBER}_session.json")
if [[ -n "$PR_URL" ]]; then
    echo "PR: $PR_URL"
fi
