#!/bin/bash
# tools/shell/jules_audit.sh
# Efficiently audits Jules sessions and identifies those needing attention.

set -e

SESSION_DIR="jules_sessions"
TMP_AUDIT="/tmp/jules_audit_$(date +%s).txt"

echo "### Jules Session Audit Report ($(date)) ###" > "$TMP_AUDIT"
echo "" >> "$TMP_AUDIT"

# Categorize sessions
echo "--- Sessions Needing Action ---" >> "$TMP_AUDIT"

# 1. Awaiting Approval/Feedback
echo "[AWAITING ACTION]" >> "$TMP_AUDIT"
jq -r 'select(.state == "AWAITING_PLAN_APPROVAL" or .state == "AWAITING_USER_FEEDBACK") | "- \(.id): \(.title) (\(.state))"' "$SESSION_DIR"/*.json >> "$TMP_AUDIT" || true
echo "" >> "$TMP_AUDIT"

# 2. Completed without PR
echo "[COMPLETED WITHOUT PR]" >> "$TMP_AUDIT"
# We check if .outputs exists and if it contains a pullRequest with a url
jq -r 'select(.state == "COMPLETED") | if (.outputs | length > 0) and (any(.outputs[]; .pullRequest.url != null)) then empty else "- \(.id): \(.title)" end' "$SESSION_DIR"/*.json >> "$TMP_AUDIT" || true
echo "" >> "$TMP_AUDIT"

# 3. Failed sessions
echo "[FAILED SESSIONS]" >> "$TMP_AUDIT"
jq -r 'select(.state == "FAILED") | "- \(.id): \(.title)"' "$SESSION_DIR"/*.json >> "$TMP_AUDIT" || true
echo "" >> "$TMP_AUDIT"

# 4. In-progress sessions (potential timeouts)
echo "[IN PROGRESS]" >> "$TMP_AUDIT"
jq -r 'select(.state == "IN_PROGRESS" or .state == "QUEUED") | "- \(.id): \(.title) (\(.state))"' "$SESSION_DIR"/*.json >> "$TMP_AUDIT" || true
echo "" >> "$TMP_AUDIT"

# Display Summary
cat "$TMP_AUDIT"
rm "$TMP_AUDIT"
