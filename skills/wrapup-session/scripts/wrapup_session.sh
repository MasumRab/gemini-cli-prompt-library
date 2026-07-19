#!/bin/bash
# Wrapup Session Script
# Generates session summary reports
# Usage: wrapup-session.sh [--output-format <format>] [--include-qa-status] [--post-to-pr]

set -euo pipefail

# Validate dependencies
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "Error: GITHUB_TOKEN environment variable is not set" >&2
    echo "Run: export GITHUB_TOKEN='your_github_token'" >&2
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed." >&2
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)" >&2
    exit 1
fi

OUTPUT_FORMAT="markdown"
INCLUDE_QA_STATUS=false
POST_TO_PR=false
OUTPUT_FILE=""
REPO=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --output-format) OUTPUT_FORMAT="$2"; shift 2 ;;
        --include-qa-status) INCLUDE_QA_STATUS=true; shift ;;
        --post-to-pr) POST_TO_PR=true; shift ;;
        --output-file) OUTPUT_FILE="$2"; shift 2 ;;
        --repo) REPO="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Auto-detect model from environment or git history
detect_model() {
    # Check common model env vars
    for var in LLM_MODEL ANTHROPIC_MODEL OPENAI_MODEL CLAUDE_MODEL GEMINI_MODEL QWEN_MODEL AZURE_OPENAI_MODEL; do
        if [[ -n "${!var:-}" ]]; then
            echo "${!var}"
            return 0
        fi
    done
    
    # Check LiteLLM env vars (API_KEY presence indicates provider)
    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        echo "openai (via OPENAI_API_KEY)"
        return 0
    fi
    if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        echo "anthropic (via ANTHROPIC_API_KEY)"
        return 0
    fi
    if [[ -n "${AZURE_API_KEY:-}" ]]; then
        echo "azure (via AZURE_API_KEY)"
        return 0
    fi
    
    # Check git commit messages for model hints (not reliable, but gives context)
    if git log --oneline -3 2>/dev/null | grep -iqE "claude|gemini|qwen|gpt|anthropic|openai|llm"; then
        echo "model-from-git-history"
        return 0
    fi
    
    # Check if running in OpenHands agent
    if [[ -n "${OPENHANDS:-}" || -n "${AGENT_NAME:-}" ]]; then
        echo "${AGENT_NAME:-OpenHands}"
        return 0
    fi
    
    echo "unknown"
}

MODEL=$(detect_model)

# Auto-detect repo
if [[ -z "$REPO" ]]; then
    REPO=$(git remote get-url origin 2>/dev/null | sed 's|.*github\.com[:/]||' | sed 's|\.git$||' || echo "")
fi

[[ -z "$REPO" ]] && { echo "Error: Could not determine repo. Use --repo owner/repo"; exit 1; }

echo "Session Wrapup"
echo "  Format: $OUTPUT_FORMAT"
echo "  Model: $MODEL"
echo "  Include QA: $INCLUDE_QA_STATUS"
echo "  Post to PR: $POST_TO_PR"
echo ""

# Get current branch changes
echo "Analyzing session changes..."
CHANGES=$(git status --porcelain 2>/dev/null || echo "")
ADDED=$(echo "$CHANGES" | grep "^??" | wc -l | tr -d ' ')
MODIFIED=$(echo "$CHANGES" | grep "^[ MAMD]" | wc -l | tr -d ' ')
DELETED=$(echo "$CHANGES" | grep "^D" | wc -l | tr -d ' ')

echo "  Files added: $ADDED"
echo "  Files modified: $MODIFIED"
echo "  Files deleted: $DELETED"

# Generate report
case "$OUTPUT_FORMAT" in
    markdown)
        echo ""
        echo "## Session Summary"
        echo ""
        echo "| Metric | Value |"
        echo "|-------|-------|"
        echo "| Files Added | $ADDED |"
        echo "| Files Modified | $MODIFIED |"
        echo "| Files Deleted | $DELETED |"
        echo ""
        
        if [[ "$INCLUDE_QA_STATUS" == "true" ]]; then
            echo "## QA Status"
            echo "  (QA integration - stub)"
            echo ""
        fi
        
        echo "## Changed Files"
        echo "$CHANGES" | head -20
        ;;
    json)
        echo ""
        echo '{'
        echo "  \"added\": $ADDED,"
        echo "  \"modified\": $MODIFIED,"
        echo "  \"deleted\": $DELETED,"
        echo "  \"repo\": \"$REPO\""
        echo '}'
        ;;
    *)
        echo "Error: Unknown format: $OUTPUT_FORMAT" >&2
        exit 1
        ;;
esac

# Save to file if requested
if [[ -n "$OUTPUT_FILE" ]]; then
    echo "Saving to $OUTPUT_FILE..."
    # Stub - would save output to file
fi

# Post to PR if requested
if [[ "$POST_TO_PR" == "true" ]]; then
    echo ""
    echo "Posting to PR..."
    echo "  (PR posting - stub)"
fi

echo ""
echo "Wrapup complete."