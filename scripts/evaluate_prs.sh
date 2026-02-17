#!/bin/bash
set -e

# Helper script to evaluate a PR
# Usage: ./scripts/evaluate_prs.sh <PR_NUMBER>

PR_NUMBER=$1

if [ -z "$PR_NUMBER" ]; then
    echo "Usage: $0 <PR_NUMBER>"
    exit 1
fi

echo "Evaluating PR #$PR_NUMBER..."

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "Error: gh (GitHub CLI) is not installed."
    exit 1
fi

# Ask if user wants to stash changes
read -p "Stash current changes? (y/N) " stash_changes
if [[ "$stash_changes" =~ ^[Yy]$ ]]; then
    git stash
fi

ORIGINAL_BRANCH=$(git branch --show-current)

# Checkout PR
echo "Checking out PR #$PR_NUMBER..."
gh pr checkout "$PR_NUMBER"

# Install dependencies?
read -p "Install dependencies from requirements.txt? (y/N) " install_deps
if [[ "$install_deps" =~ ^[Yy]$ ]]; then
    pip install -r requirements.txt
fi

# Run tests
echo "Running tests..."
pytest || echo "Tests FAILED!"

# Manual check prompt
read -p "Perform manual checks? (Press Enter to continue, Ctrl+C to abort) " manual_check

# Decision
read -p "Are you satisfied with this PR? (y/N) " pr_status
if [[ "$pr_status" =~ ^[Yy]$ ]]; then
    read -p "Approve and Merge? (y/N) " merge_pr
    if [[ "$merge_pr" =~ ^[Yy]$ ]]; then
        gh pr merge "$PR_NUMBER" --merge --delete-branch
        echo "PR merged."
        if [ -n "$ORIGINAL_BRANCH" ]; then
             git checkout "$ORIGINAL_BRANCH"
        fi
        exit 0
    else
        echo "PR approved locally but NOT merged."
    fi
else
    echo "PR evaluation finished. Please provide feedback on GitHub."
fi

read -p "Switch back to original branch ($ORIGINAL_BRANCH)? (Y/n) " switch_back
if [[ "$switch_back" =~ ^[Yy]$ ]] || [ -z "$switch_back" ]; then
    if [ -n "$ORIGINAL_BRANCH" ]; then
        git checkout "$ORIGINAL_BRANCH"
    else
        echo "Could not determine original branch."
    fi
fi

if [[ "$stash_changes" =~ ^[Yy]$ ]]; then
    read -p "Pop stash? (y/N) " pop_stash
    if [[ "$pop_stash" =~ ^[Yy]$ ]]; then
        git stash pop
    fi
fi
