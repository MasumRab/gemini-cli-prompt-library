#!/bin/bash
# Pre-Flight Validation Script
set -e

# Parse arguments
AUTO_CONFIRM=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--auto-confirm)
            AUTO_CONFIRM=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🛡️  Running Pre-Flight Checks..."

# 1. Auth Check
echo "1. Checking Authentication..."
python3 "$(dirname "$0")/auth_manager.py" || exit 1

# Helper function for confirm prompts
prompt_confirm() {
    local message="$1"
    if [ "$AUTO_CONFIRM" = true ]; then
        echo "(Auto-confirm enabled, skipping)"
        return 0
    fi
    read -p "$message (y/n): " confirm
    if [[ ! "$confirm" =~ ^[yY]$ ]]; then exit 1; fi
}

# 2. Dirty State Check
echo "2. Checking for Uncommitted Changes..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  WARNING: Working directory is dirty."
    prompt_confirm "Continue anyway?"
else
    echo "✅ Working directory clean."
fi

# 3. Branch Check
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
# Dynamically detect default branch from remote HEAD
DEFAULT_BRANCH=$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo "main")
DEFAULT_BRANCH=${DEFAULT_BRANCH#origin/}
if [ "$CURRENT_BRANCH" == "$DEFAULT_BRANCH" ]; then
    echo "⚠️  WARNING: You are on the default branch ($DEFAULT_BRANCH)."
    prompt_confirm "Are you sure you want to run agent tasks on $DEFAULT_BRANCH?"
fi

echo "✅ Pre-flight checks passed."
