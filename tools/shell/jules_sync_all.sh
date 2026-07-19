#!/bin/bash
# scripts/jules_sync_all.sh
# Syncs local Jules session metadata with the latest API state.

set -e

if [ -z "$JULES_API_KEY" ]; then
  echo "Error: JULES_API_KEY environment variable is not set."
  exit 1
fi

mkdir -p jules_sessions

echo "Step 1: Syncing local sessions..."
# Find all local session files
for session_file in jules_sessions/jules_*.json jules_sessions/pr*_session.json; do
  [ -e "$session_file" ] || continue
  id=$(jq -r '.id' "$session_file")
  echo "Syncing $id..."
  curl -s "https://jules.googleapis.com/v1alpha/sessions/$id" \
    -H "x-goog-api-key: $JULES_API_KEY" > "jules_sessions/jules_${id}.json"
done

echo "Step 2: Checking for new remote sessions..."
# Fetch the 20 most recent sessions and save any that aren't already synced
curl -s "https://jules.googleapis.com/v1alpha/sessions?pageSize=20" \
  -H "x-goog-api-key: $JULES_API_KEY" | jq -c '.sessions[]' | while read -r session; do
    id=$(echo "$session" | jq -r '.name | split("/")[-1]')
    if [ ! -f "jules_sessions/jules_${id}.json" ]; then
      echo "New session found: $id. Saving..."
      echo "$session" > "jules_sessions/jules_${id}.json"
    fi
done

echo "Done! All session metadata refreshed in jules_sessions/."
