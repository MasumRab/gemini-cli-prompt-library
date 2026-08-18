#!/usr/bin/env bash
# Compare functionality across .graphite-agent versions
# Usage: compare_versions.sh <version1> <version2> [version3...]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKTREES_DIR="$REPO_ROOT/.worktrees"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <version1> <version2> [version3...]"
    echo "Example: $0 v64 v72 v73"
    echo ""
    echo "Available versions:"
    for d in "$WORKTREES_DIR"/*/; do
        version=$(basename "$d")
        if [ -f "$d/.graphite-agent/VERSION_README.md" ]; then
            desc=$(grep -m1 "# $version" "$d/.graphite-agent/VERSION_README.md" | sed 's/# $version - //')
            echo "  $version - $desc"
        fi
    done
    exit 1
fi

echo "=== .graphite-agent Version Comparison ==="
echo "Comparing: $*"
echo ""

# Create temp dir for outputs
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# Run each version and capture output
for version in "$@"; do
    worktree_path="$WORKTREES_DIR/$version"

    if [ ! -d "$worktree_path" ]; then
        echo "⚠ Worktree for $version not found at $worktree_path"
        echo "  Run setup_worktrees.sh first"
        continue
    fi

    echo "--- $version ---"
    cd "$worktree_path"

    # Run analysis
    if [ -f ".graphite-agent/tools/analyse.py" ]; then
        echo "Running analysis..."
        python3 .graphite-agent/tools/analyse.py > "$TMPDIR/${version}_analysis.json" 2>&1 || true
        echo "Analysis output: $TMPDIR/${version}_analysis.json"
    fi

    # Run target discovery
    if [ -f ".graphite-agent/tools/discover_targets.py" ]; then
        echo "Running target discovery..."
        python3 .graphite-agent/tools/discover_targets.py > "$TMPDIR/${version}_targets.json" 2>&1 || true
        echo "Target output: $TMPDIR/${version}_targets.json"
    fi

    # Run root health
    if [ -f ".graphite-agent/tools/root_health.py" ]; then
        echo "Running root health..."
        python3 .graphite-agent/tools/root_health.py > "$TMPDIR/${version}_root_health.json" 2>&1 || true
        echo "Root health output: $TMPDIR/${version}_root_health.json"
    fi

    # Run stack order
    if [ -f ".graphite-agent/tools/stack_order.py" ]; then
        echo "Running stack order..."
        python3 .graphite-agent/tools/stack_order.py > "$TMPDIR/${version}_stack.json" 2>&1 || true
        echo "Stack output: $TMPDIR/${version}_stack.json"
    fi

    # Run validation
    if [ -f ".graphite-agent/tools/validate_plan.py" ]; then
        echo "Running validation..."
        python3 .graphite-agent/tools/validate_plan.py > "$TMPDIR/${version}_validation.json" 2>&1 || true
        echo "Validation output: $TMPDIR/${version}_validation.json"
    fi

    echo ""
done

# Summary comparison
echo "=== Comparison Summary ==="
echo ""
echo "Files generated in $TMPDIR:"
ls -la "$TMPDIR"
echo ""
echo "To compare outputs side-by-side:"
for version in "$@"; do
    echo "  $version: $TMPDIR/${version}_*.json"
done
echo ""
echo "To view differences:"
for output in analysis targets root_health stack validation; do
    files=""
    for version in "$@"; do
        file="$TMPDIR/${version}_${output}.json"
        if [ -f "$file" ]; then
            files="$files $file"
        fi
    done
    if [ -n "$files" ]; then
        echo "  diff $files"
    fi
done
