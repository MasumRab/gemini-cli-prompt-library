#!/bin/bash
set -euo pipefail

echo "Testing Jules API standardized setup..."

# Check for API key (allowing fallback via script's own logic but warning here if both missing)
if [ -z "${JULES_API_KEY:-}" ] && [ -z "${JULES_API_KET:-}" ]; then
  echo "Error: Neither JULES_API_KEY nor JULES_API_KET is set."
  exit 1
fi

echo "Running Jules API connection test..."
uv run python -m tools.tests.test_api_connection

echo "Running all features test..."
uv run python -m tools.tests.test_all_features

echo "Testing CLI scripts..."
# Just check if they can be imported and show help
uv run python -m tools.sessions.jules_list_sessions --help > /dev/null
uv run python -m tools.pr.jules_audit_session_pr --help > /dev/null

echo "All tests passed!"