#!/bin/bash
# Analyze local Jules session JSON files
# Usage:
#   ./analyze_sessions.sh --status      # All sessions with state
#   ./analyze_sessions.sh --pr-links     # PR URLs only
#   ./analyze_sessions.sh --pending      # Sessions needing action
#   ./analyze_sessions.sh --summary      # One-line per session
#   ./analyze_sessions.sh --extract-patch # Extract patches to ./patches/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSIONS_DIR="${JULES_SESSIONS_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)/jules_sessions}"

# Default to ~/jules_sessions if not in a git repo
if [[ ! -d "$SESSIONS_DIR" ]]; then
    SESSIONS_DIR="$HOME/jules_sessions"
fi

cmd="${1:---status}"

case "$cmd" in
    --status)
        echo "=== Jules Sessions Status ==="
        echo "Location: $SESSIONS_DIR"
        echo ""
        if [[ ! -d "$SESSIONS_DIR" ]]; then
            echo "No sessions directory found"
            exit 1
        fi
        for f in "$SESSIONS_DIR"/*_session.json; do
            [[ -f "$f" ]] || continue
            id=$(basename "$f" | sed 's/pr\([0-9]*\)_session.json/\1/')
            jq -r '"\(.state | .[0:10]) | PR #'"$id"' | \(.title[0:50])"' "$f" 2>/dev/null
        done | column -t -s '|'
        ;;
    
    --pr-links)
        echo "=== PR Links ==="
        for f in "$SESSIONS_DIR"/*_session.json; do
            [[ -f "$f" ]] || continue
            id=$(basename "$f" | sed 's/pr\([0-9]*\)_session.json/\1/')
            url=$(jq -r '.outputs[]?.pullRequest?.url // empty' "$f" 2>/dev/null)
            if [[ -n "$url" ]]; then
                echo "PR #$id: $url"
            fi
        done
        ;;
    
    --pending)
        echo "=== Sessions Needing Action ==="
        for f in "$SESSIONS_DIR"/*_session.json; do
            [[ -f "$f" ]] || continue
            jq -r 'select(.state == "AWAITING_PLAN_APPROVAL" or .state == "IN_PROGRESS" or .state == "QUEUED") |
                   "\(.state) | \(.id) | \(.title[0:40])"' "$f" 2>/dev/null
        done | column -t -s '|'
        ;;
    
    --summary)
        echo "=== Session Summary ==="
        for f in "$SESSIONS_DIR"/*_session.json; do
            [[ -f "$f" ]] || continue
            id=$(basename "$f" | sed 's/pr\([0-9]*\)_session.json/\1/')
            jq -r '"\(.state) | \(.sourceContext.githubRepoContext.startingBranch // "repoless") | PR #'"$id"' | \(.title[0:35])"' "$f" 2>/dev/null
        done | column -t -s '|'
        ;;
    
    --extract-patch)
        OUTPUT_DIR="${2:-./patches}"
        mkdir -p "$OUTPUT_DIR"
        echo "=== Extracting Patches to $OUTPUT_DIR ==="
        for f in "$SESSIONS_DIR"/*_session.json; do
            [[ -f "$f" ]] || continue
            id=$(basename "$f" | sed 's/pr\([0-9]*\)_session.json/\1/')
            patch=$(jq -r '.outputs[].changeSet.gitPatch // empty' "$f" 2>/dev/null)
            if [[ -n "$patch" ]]; then
                echo "$patch" > "$OUTPUT_DIR/pr${id}.patch"
                echo "Extracted: pr${id}.patch"
            fi
        done
        ;;
    
    --stats)
        echo "=== Session Statistics ==="
        total=0
        completed=0
        failed=0
        running=0
        for f in "$SESSIONS_DIR"/*_session.json; do
            [[ -f "$f" ]] || continue
            total=$((total + 1))
            state=$(jq -r '.state' "$f" 2>/dev/null)
            case "$state" in
                COMPLETED) completed=$((completed + 1)) ;;
                FAILED) failed=$((failed + 1)) ;;
                IN_PROGRESS|QUEUED|AWAITING_PLAN_APPROVAL|AWAITING_USER_FEEDBACK) running=$((running + 1)) ;;
            esac
        done
        echo "Total: $total"
        echo "Completed: $completed"
        echo "Failed: $failed"
        echo "In Progress: $running"
        ;;
    
    --by-branch)
        branch="${2:-scientific}"
        echo "=== Sessions on branch: $branch ==="
        for f in "$SESSIONS_DIR"/*_session.json; do
            [[ -f "$f" ]] || continue
            jq -r "select(.sourceContext.githubRepoContext.startingBranch == \"$branch\") | 
                   \"\(.state) | \(.title[0:50])\"" "$f" 2>/dev/null
        done | column -t -s '|'
        ;;
    
    -h|--help|*)
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  --status        List all sessions with state"
        echo "  --pr-links      List all PR URLs"
        echo "  --pending       Show sessions needing action"
        echo "  --summary       One-line summary per session"
        echo "  --stats         Count by status"
        echo "  --extract-patch Extract git patches to ./patches/"
        echo "  --by-branch BR  Filter by branch name"
        echo ""
        echo "Environment:"
        echo "  JULES_SESSIONS_DIR  Override sessions directory (default: ./jules_sessions)"
        ;;
esac
