#!/usr/bin/env bash
# Setup parallel worktrees for .graphite-agent version development
# Creates isolated worktrees for v64, v72, and v73 parallel development

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GRAPHITE_DIR="$REPO_ROOT/.graphite-agent"
WORKTREES_DIR="$REPO_ROOT/.worktrees"

echo "=== Setting up .graphite-agent parallel worktrees ==="
echo "Repo root: $REPO_ROOT"
echo "Graphite dir: $GRAPHITE_DIR"
echo "Worktrees dir: $WORKTREES_DIR"

# Create worktrees directory
mkdir -p "$WORKTREES_DIR"

# Define version branches and their specs
declare -A VERSION_SPECS
VERSION_SPECS[v64]="V6.4 Topology Audit - base topology audit engine with multi-root support"
VERSION_SPECS[v72]="V7.2 Human-in-the-Loop Automation - target analysis, root health, stack ordering"
VERSION_SPECS[v73]="V7.3 Derived-Output Mode - reads existing snapshot/plan, writes derived outputs"

# Create worktree for each version
for version in v64 v72 v73; do
    worktree_path="$WORKTREES_DIR/$version"
    branch_name="version/$version"

    echo ""
    echo "--- Setting up $version worktree ---"

    # Remove existing worktree if present
    if [ -d "$worktree_path" ]; then
        echo "Removing existing worktree at $worktree_path"
        git worktree remove "$worktree_path" --force 2>/dev/null || true
    fi

    # Create new worktree
    echo "Creating worktree at $worktree_path"
    git worktree add "$worktree_path" -b "$branch_name"

    # Copy version-specific fixtures
    if [ -d "$GRAPHITE_DIR/fixtures/$version" ]; then
        echo "Copying $version fixtures"
        mkdir -p "$worktree_path/.graphite-agent/fixtures/$version"
        cp -r "$GRAPHITE_DIR/fixtures/$version/"* "$worktree_path/.graphite-agent/fixtures/$version/"
    fi

    # Create version-specific README
    cat > "$worktree_path/.graphite-agent/VERSION_README.md" << EOF
# $version - ${VERSION_SPECS[$version]}

## Worktree Information
- **Path**: $worktree_path
- **Branch**: $branch_name
- **Version**: $version

## Development
This worktree is isolated for parallel $version development.

## Run Tests
\`\`\`bash
cd $worktree_path
python3 -m unittest discover -s .graphite-agent/tests/ -v
\`\`\`

## Version-Specific Notes
$(if [ "$version" = "v64" ]; then echo "- Base topology audit with multi-root support"; fi)
$(if [ "$version" = "v72" ]; then echo "- Adds human-in-the-loop automation"; fi)
$(if [ "$version" = "v73" ]; then echo "- Derived-output mode on top of v64/v72 inputs"; fi)
EOF

    echo "✓ $version worktree ready at $worktree_path"
done

echo ""
echo "=== Worktree Setup Complete ==="
echo ""
echo "Worktrees created:"
for version in v64 v72 v73; do
    echo "  $version: $WORKTREES_DIR/$version (branch: version/$version)"
done
echo ""
echo "To switch between versions:"
echo "  cd $WORKTREES_DIR/v64   # V6.4 topology audit"
echo "  cd $WORKTREES_DIR/v72   # V7.2 human-in-the-loop"
echo "  cd $WORKTREES_DIR/v73   # V7.3 derived outputs"
echo ""
echo "To compare functionality across versions:"
echo "  $WORKTREES_DIR/v64/.graphite-agent/scripts/compare_versions.sh v64 v72 v73"
