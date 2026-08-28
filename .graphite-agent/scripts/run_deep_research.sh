#!/usr/bin/env bash
# Queue improved deep research prompt for execution
# This script validates the prompt file exists and prepares it for review

PROMPT_FILE=".graphite-agent/docs/DEEP_RESEARCH_PROMPT.md"
TARGET_DIR=".graphite-agent"

echo "=== Deep Research Prompt Execution Queue ==="
echo "Prompt file: $PROMPT_FILE"
echo "Target directory: $TARGET_DIR"
echo ""

if [ ! -f "$PROMPT_FILE" ]; then
    echo "ERROR: Prompt file not found at $PROMPT_FILE"
    exit 1
fi

echo "Prompt file exists. Contents:"
echo "---"
cat "$PROMPT_FILE"
echo "---"
echo ""
echo "Ready for execution. Use this prompt with deep research tooling."
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
