#!/bin/bash
set -e
IDS=$(grep -oE "[0-9]{18,}" .jules/session_analysis/tmp/problematic_sessions.txt)
mkdir -p .jules/session_analysis/details

for id in $IDS; do
  if [ ! -f ".jules/session_analysis/details/session_${id}.json" ]; then
    echo "Retrieving session $id..."
    curl -s "https://jules.googleapis.com/v1alpha/sessions/$id" \
      -H "x-goog-api-key: $JULES_API_KEY" \
      > ".jules/session_analysis/details/session_${id}.json"
    # Sleep to be polite to the API
    sleep 1
  fi
done
