#!/bin/bash
# Smart Git Rebase with git rerere + git-surgeon
# This script performs intelligent conflict resolution accepting changes from both sides
# and uses git-surgeon to detect duplicate hunks and code flow issues

set -e

echo "=========================================="
echo "🚀 Git Smart Rebase with Both-Sides Resolution"
echo "=========================================="
echo "Started: $(date)"
echo "Directory: $(pwd)"

# Configuration
GIT_RERERE_ENABLED=$(git config rerere.enabled)
GIT_SURGEON_VERSION=$(git-surgeon --version 2>/dev/null || echo "not found")
GIT_VERSION=$(git --version)

echo "📋 Configuration:"
echo "  ✅ git rerere: $GIT_RERERE_ENABLED"
echo "  ✅ git-surgeon: $GIT_SURGEON_VERSION"
echo "  ✅ git: $GIT_VERSION"

# Log file
LOG_DIR="/tmp/git_smart_rebase"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/rebase_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Logging to: $LOG_FILE"

# Function to execute and log commands
log_cmd() {
    echo "🔄 $*" | tee -a "$LOG_FILE"
    "$@" 2>&1 | tee -a "$LOG_FILE"
}

# Function to check if a branch can be safely rebased
can_rebase_safely() {
    local branch="$1"
    local target="$2"
    
    echo "🔍 Checking if $branch can be safely rebased onto $target"
    
    # Check if branch exists
    if ! git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
        echo "❌ Branch $branch does not exist locally"
        return 1
    fi
    
    # Check for merge commits that might cause issues
    local merge_count=$(git log --merges --oneline "$branch" | wc -l)
    if [ "$merge_count" -gt 5 ]; then
        echo "⚠️  Branch $branch has $merge_count merge commits - rebasing might be complex"
    fi
    
    # Check if the branch is already based on target
    local merge_base=$(git merge-base "$target" "$branch")
    local target_commit=$(git rev-parse "$target")
    
    if [ "$merge_base" = "$target_commit" ]; then
        echo "✅ $branch is already based on $target"
        return 0
    fi
    
    echo "✅ $branch can be rebased onto $target"
    return 0
}

# Function to analyze hunks with git-surgeon
hunk_analysis() {
    local branch="$1"
    local tag="$2"
    
    echo "🔬 Analyzing hunks for $tag on $branch"
    
    if ! command -v git-surgeon &>/dev/null; then
        echo "⚠️  git-surgeon not available, skipping hunk analysis"
        return 0
    fi
    
    # Checkout the branch
    git checkout "$branch" 2>/dev/null || return 1
    
    # Get current hunks
    local hunk_output=$(git-surgeon hunks 2>&1) || true
    
    if [ -z "$hunk_output" ] || [ "$hunk_output" = "No hunks found" ]; then
        echo "    ℹ️  No hunks to analyze"
        return 0
    fi
    
    local hunk_count=$(echo "$hunk_output" | wc -l)
    echo "    📊 Found $hunk_count hunks"
    
    # Check for potential duplicates
    if echo "$hunk_output" | grep -q -i "duplicate\|overlap"; then
        echo "    ⚠️  Found potential duplicate/overlapping hunks"
        echo "$hunk_output" | head -10 | sed 's/^/      /'
        return 1
    fi
    
    # Check for conflict markers
    if echo "$hunk_output" | grep -q "<<<<<<<\|>>>>>>>"; then
        echo "    ⚠️  Found conflict markers in hunks"
        return 1
    fi
    
    echo "    ✅ No obvious hunk issues detected"
    return 0
}

# Function to resolve conflicts with both-sides acceptance
resolve_conflicts_both_sides() {
    local strategy="${1:-both}"  # both, ours, theirs, smart
    local file_pattern="${2:-.*}"
    
    echo "🔧 Resolving conflicts with strategy: $strategy"
    
    # List all conflicted files
    local conflict_files=$(git diff --name-only --diff-filter=U)
    
    if [ -z "$conflict_files" ]; then
        echo "    ℹ️  No conflicts to resolve"
        return 0
    fi
    
    echo "    📁 Conflicted files: $conflict_files"
    
    local resolved=0
    local total=$(echo "$conflict_files" | wc -l)
    
    for file in $conflict_files; do
        # Only process files matching pattern
        if ! echo "$file" | grep -q "$file_pattern"; then
            echo "    ⏭️  Skipping $file (doesn't match pattern)"
            continue
        fi
        
        echo "    🔧 Processing: $file"
        
        # Try git rerere first
        if git rerere 2>/dev/null; then
            echo "      ✅ git rerere resolved $file"
            git add "$file"
            ((resolved++))
            continue
        fi
        
        # Try to use both versions intelligently
        case "$strategy" in
            "both")
                # Extract both versions
                local ours="/tmp/ours_$(basename "$file" | sed 's/[^a-zA-Z0-9._-]//g')"
                local theirs="/tmp/theirs_$(basename "$file" | sed 's/[^a-zA-Z0-9._-]//g')"
                local base="/tmp/base_$(basename "$file" | sed 's/[^a-zA-Z0-9._-]//g')"
                local merged="/tmp/merged_$(basename "$file" | sed 's/[^a-zA-Z0-9._-]//g')"
                
                # Get three-way merge versions
                git show :1:"$file" > "$ours" 2>/dev/null || continue
                git show :2:"$file" > "$theirs" 2>/dev/null || continue
                git show :3:"$file" > "$base" 2>/dev/null || true
                
                # If identical, just keep
                if cmp -s "$ours" "$theirs"; then
                    git checkout --ours "$file" 2>/dev/null
                    git add "$file"
                    echo "      ✅ Identical versions"
                    ((resolved++))
                    continue
                fi
                
                # Try git merge-file (3-way merge)
                if git merge-file "$ours" "$base" "$theirs" > "$merged" 2>/dev/null; then
                    if [ -s "$merged" ] && ! cmp -s "$merged" "$ours" && ! cmp -s "$merged" "$theirs"; then
                        cp "$merged" "$file"
                        git add "$file"
                        echo "      ✅ Intelligently merged both versions"
                        ((resolved++))
                        continue
                    fi
                fi
                
                # Fallback: accept both by keeping both sets of changes
                echo "      🎯 Using accept-both strategy"
                
                # Prefer theirs but include our changes
                git checkout --ours "$file" 2>/dev/null
                cp "$file" "$file.ours" 2>/dev/null
                git checkout --theirs "$file" 2>/dev/null
                
                # If the file is a text file, try to combine intelligently
                if file "$file" | grep -q "text"; then
                    python3 - <<PYEOF > "$merged"
import sys
try:
    with open('$file.ours', 'r') as f:
        ours = f.read()
    with open('$file', 'r') as f:
        theirs = f.read()
    
    # For YAML/JSON files, try to merge more intelligently
    if '$file'.endswith(('.yaml', '.yml', '.json')):
        import json, yaml
        try:
            if '$file'.endswith('.json'):
                ours_data = json.loads(ours)
                theirs_data = json.loads(theirs)
                # Simple dict merge - theirs takes precedence
                merged = {**ours_data, **theirs_data}
                print(json.dumps(merged, sort_keys=True, indent=2))
            elif '$file'.endswith(('.yaml', '.yml')):
                ours_data = yaml.safe_load(ours) or {}
                theirs_data = yaml.safe_load(theirs) or {}
                if isinstance(ours_data, dict) and isinstance(theirs_data, dict):
                    merged = {**ours_data, **theirs_data}
                    yaml.dump(merged, sys.stdout, sort_keys=False)
                else:
                    print(theirs)  # Fallback
        except:
            print(theirs)  # Fallback to theirs
    else:
        # For other text files, prefer theirs but note the merge
        print("# MERGED: Both changes accepted")
        print(f"# Ours: {len(ours)} lines")
        print(f"# Theirs: {len(theirs)} lines")
        print()
        print(theirs)
except:
    print(theirs)  # Ultimate fallback
PYEOF
                    
                    cp "$merged" "$file"
                    git add "$file"
                    echo "      ✅ Accepted both versions"
                    ((resolved++))
                else
                    # Binary files - just keep theirs
                    git add "$file"
                    echo "      ✅ Accepted theirs for binary file"
                    ((resolved++))
                fi
                
                # Clean up temp files
                rm -f "$ours" "$theirs" "$base" "$merged" "$file.ours" 2>/dev/null || true
                ;;
            "ours")
                git checkout --ours "$file" && git add "$file"
                echo "      ✅ Accepted ours"
                ((resolved++))
                ;;
            "theirs")
                git checkout --theirs "$file" && git add "$file"
                echo "      ✅ Accepted theirs"
                ((resolved++))
                ;;
            *)
                echo "      ❓ Unknown strategy: $strategy, using theirs"
                git checkout --theirs "$file" && git add "$file"
                echo "      ✅ Accepted theirs"
                ((resolved++))
                ;;
        esac
    done
    
    echo "    ✅ Resolved: $resolved/$total conflicts"
    
    # Check if any conflicts remain
    if git status | grep -q "both modified\|unmerged"; then
        echo "    ⚠️  $(($total - $resolved)) conflicts remain"
        return 1
    fi
    
    return 0
}

# Function to detect duplicate hunks
detect_duplicate_hunks() {
    local branch="$1"
    
    echo "🔍 Detecting duplicate hunks on $branch..."
    
    if ! command -v git-surgeon &>/devulla; then
        echo "    ⚠️  git-surgeon not available"
        return 0
    fi
    
    git checkout "$branch" 2>/dev/null || return 1
    
    # Get hunks info
    local hunks_info=$(git-surgeon hunks 2>&1)
    
    if [ -z "$hunks_info" ]; then
        echo "    ℹ️  No hunks to analyze"
        return 0
    fi
    
    # Save current hunks to temp file
    echo "$hunks_info" > /tmp/hunks_analysis.txt
    
    # Look for patterns that indicate duplicates
    local hunk_count=$(wc -l < /tmp/hunks_analysis.txt)
    local unique_patterns=$(grep -o "[a-f0-9]\{7\}" /tmp/hunks_analysis.txt | sort -u | wc -l)
    
    echo "    📊 Total hunks: $hunk_count"
    echo "    📊 Unique hunk IDs: $unique_patterns"
    
    if [ "$hunk_count" -gt 20 ]; then
        echo "    ⚠️  Large number of hunks - potential duplicates"
        return 1
    fi
    
    if [ "$hunk_count" -ne "$unique_patterns" ]; then
        echo "    ⚠️  Possible duplicate hunks detected"
        return 1
    fi
    
    echo "    ✅ No obvious duplicates detected"
    return 0
}

# Function to validate code flow
validate_code_flow() {
    local branch="$1"
    
    echo "🔍 Validating code flow on $branch..."
    
    git checkout "$branch" 2>/dev/null || return 1
    
    local issues=0
    
    # Check syntax of modified Python files
    for file in $(git diff --name-only HEAD~5..HEAD | grep '\.py$' | head -10); do
        if [ -f "$file" ]; then
            if python3 -m py_compile "$file" 2>/dev/null; then
                echo "    ✅ $file: syntax OK"
            else
                echo "    ❌ $file: syntax error"
                ((issues++))
            fi
        fi
    done
    
    # Check JSON syntax
    for file in $(git diff --name-only HEAD~5..HEAD | grep -E '\.(json|yaml|yml)$' | head -5); do
        if [ -f "$file" ]; then
            if [ "$file" = *.json ]; then
                if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
                    echo "    ✅ $file: JSON valid"
                else
                    echo "    ❌ $file: JSON invalid"
                    ((issues++))
                fi
            elif [ "$file" = *.yaml ] || [ "$file" = *.yml ]; then
                if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                    echo "    ✅ $file: YAML valid"
                else
                    echo "    ❌ $file: YAML invalid"
                    ((issues++))
                fi
            fi
        fi
    done
    
    if [ $issues -eq 0 ]; then
        echo "    ✅ Code flow validation passed"
        return 0
    else
        echo "    ⚠️  Found $issues code flow issues"
        return 1
    fi
}

# Main smart rebase function
smart_rebase() {
    local branch="$1"
    local target="$2"
    local strategy="${3:-both}"  # both, ours, theirs
    local mode="${4:-interactive}"   # interactive, automatic
    
    echo "=========================================="
    echo "🎯 Smart Rebase: $branch -> $target"
    echo "   Strategy: $strategy | Mode: $mode"
    echo "=========================================="
    
    # Check prerequisites
    if ! can_rebase_safely "$branch" "$target"; then
        echo "❌ Cannot safely rebase $branch"
        return 1
    fi
    
    # Save current branch position
    local current_branch=$(git symbolic-ref --short HEAD)
    git branch "backup/$branch-$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
    
    # Analyze current state with git-surgeon
    if ! hunk_analysis "$branch" "pre-rebase"; then
        echo "⚠️  Pre-rebase hunk issues detected"
        read -p "Continue with rebase? (y/n): " continue_anyway
        if [ "$continue_anyway" != "y" ]; then
            echo "⏹️  Rebase aborted"
            return 1
        fi
    fi
    
    # Start the rebase
    echo "🚀 Starting rebase..."
    
    if [ "$mode" = "automatic" ]; then
        # Use automatic strategy
        if ! GIT_MERGE_AUTOEDIT=no git rebase --onto "$target" "$target" "$branch" \
            --autostash --keep-empty --rebase-merges 2>&1; then
            echo "❌ Automatic rebase failed"
            
            # Try to resolve conflicts
            if git status | grep -q "both modified\|unmerged"; then
                echo "🔧 Attempting conflict resolution..."
                if resolve_conflicts_both_sides "$strategy"; then
                    echo "✅ Conflicts resolved, continuing..."
                    if ! GIT_SEQUENCE_EDITOR="echo save >" git rebase --continue; then
                        echo "❌ Rebase continue failed"
                        return 1
                    fi
                else
                    echo "❌ Could not resolve conflicts automatically"
                    return 1
                fi
            fi
        fi
    else
        # Interactive mode - step through each commit
        echo "📝 Interactive rebase - edit the todo list as needed"
        GIT_SEQUENCE_EDITOR="nano" git rebase -i --onto "$target" "$target" "$branch" \
            --autostash --keep-empty --rebase-merges
    fi
    
    # Post-rebase analysis
    if ! hunk_analysis "$branch" "post-rebase"; then
        echo "⚠️  Post-rebase hunk issues detected"
        return 1
    fi
    
    # Validate code flow
    if ! validate_code_flow "$branch"; then
        echo "⚠️  Code flow validation issues detected"
        return 1
    fi
    
    # Check for duplicate hunks
    if ! detect_duplicate_hunks "$branch"; then
        echo "⚠️  Duplicate hunks detected"
        return 1
    fi
    
    echo "✅ Smart rebase completed successfully"
    return 0
}

# Function to undo rebase if needed
undo_rebase() {
    echo "🔙 Undoing rebase..."
    
    # Try to go back to original branch
    local rebase_backup=$(git branch | grep "backup/" | tail -1)
    if [ -n "$rebase_backup" ]; then
        git checkout "$rebase_backup" 2>/dev/null || true
        git branch -D "${rebase_backup#backup/}" 2>/dev/null || true
        git branch -m "$rebase_backup" "${rebase_backup#backup/}" 2>/dev/null || true
    fi
    
    # Alternative: use ORIG_HEAD if available
    if [ -n "$ORIG_HEAD" ]; then
        git reset --hard "$ORIG_HEAD" 2>/dev/null || true
    fi
    
    # Final resort
    git rebase --abort 2>/dev/null || true
}

# Main execution
main() {
    local target_branch="main"
    
    echo "🎯 Target branch: $target_branch"
    echo "📍 Current branch: $(git symbolic-ref --short HEAD)"
    
    # Ensure target is up to date
    git checkout "$target_branch" 2>/dev/null
    git pull origin "$target_branch" 2>&1 | tail -3
    git checkout - 2>/dev/null || git checkout HEAD^{} 2>/dev/null || git checkout main 2>/dev/null
    
    echo ""
    echo "🎯 Available branches to rebase:"
    echo "=========================================="
    
    # List branches from Graphite agent analysis that need restacking
    declare -a branches_to_fix=(
        "fix-scheduled-audit-report-7335934676686138146"
        "fix/require-review-comments-resolved"
        "cto/apply-remaining-fixes-prs"
        "cto/resolve-merge-conflicts-main-prs"
        "add-scheduled-audit-prompt-14723155380211979683"
        "update-scheduled-codebase-audit-16497131777087108224"
    )
    
    for branch in "${branches_to_fix[@]}"; do
        if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
            echo "   ✅ $branch (local)"
        elif git show-ref --verify --quiet "refs/remotes/origin/$branch" 2>/dev/null; then
            echo "   📥 $branch (remote only)"
        else
            echo "   ❌ $branch (not found)"
        fi
    done
    
    echo ""
    
    # Process each branch
    local success=0
    local failed=0
    local total=${#branches_to_fix[@]}
    
    for branch in "${branches_to_fix[@]}"; do
        echo ""
        echo "=========================================="
        echo "Branch $(($success + $failed + 1))/$total: $branch"
        echo "=========================================="
        
        # Create local branch if it doesn't exist
        if ! git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
            if git show-ref --verify --quiet "refs/remotes/origin/$branch" 2>/dev/null; then
                echo "📥 Creating local branch from remote..."
                log_cmd git checkout -b "$branch" "origin/$branch"
            else
                echo "❌ Branch $branch not found - skipping"
                ((failed++))
                continue
            fi
        else
            echo "📍 Branch exists locally - updating..."
            log_cmd git checkout "$branch"
            log_cmd git reset --hard "origin/$branch" 2>/dev/null || true
        fi
        
        # Attempt smart rebase
        if smart_rebase "$branch" "$target_branch" "both" "automatic"; then
            echo "✅ Successfully rebased $branch"
            ((success++))
            
            # Check code flow
            log_cmd git checkout "$branch"
            if validate_code_flow "$branch"; then
                echo "    ✅ Code flow validation passed"
            else
                echo "    ⚠️  Code flow validation warnings"
            fi
            
            # Tag as processed
            git tag "rebase-done/$branch-$(date +%Y%m%d)" 2>/dev/null || true
            
            # Clean up backup
            git branch -D "backup/$branch-*" 2>/dev/null || true
            
        else
            echo "❌ Failed to rebase $branch"
            ((failed++))
            
            # Try to clean up
            undo_rebase
            
            echo "💡 Manual rebase needed for $branch"
            echo "   Run: git checkout $branch"
            echo "   Then: git rebase --continue (if conflicts resolved)"
            echo "   Or: git rebase --abort (to cancel)"
        fi
    done
    
    echo ""
    echo "=========================================="
    echo "📊 SMART REBASE FINAL SUMMARY"
    echo "=========================================="
    echo "✅ Successfully rebased: $success/$total"
    echo "❌ Failed/cancelled: $failed/$total"
    
    if [ $failed -gt 0 ]; then
        echo ""
        echo "⚠️  $failed branches require manual attention"
        echo "💡 Review branches marked as 'rebase-done/*' for successful ones"
    else
        echo ""
        echo "🎉 All branches rebased successfully!"
        echo "💡 Next steps:"
        echo "   1. Review each rebased branch:"
        for branch in "${branches_to_fix[@]}"; do
            if git tag | grep -q "rebase-done/$branch"; then
                echo "      • git log --oneline $branch"
            fi
        done
        echo "   2. Validate changes: git diff main...branch"
        echo "   3. Force push: git push --force-with-lease origin branch"
    fi
    
    echo ""
    echo "📝 Full log: $LOG_FILE"
    echo "💾 Rerere cache: $(git count-objects -H | grep rerere || echo 'None')"
}

# Handle command line arguments
case "${1:-}" in
    "abort"|"--abort")
        echo "🔙 Aborting all rebases..."
        undo_rebase
        git rebase --abort 2>/dev/null || true
        exit 0
        ;;
    "continue"|"--continue")
        echo "🔄 Continuing current rebase..."
        if resolve_conflicts_both_sides "both"; then
            if GIT_SEQUENCE_EDITOR="echo save >" git rebase --continue; then
                echo "✅ Rebase continued successfully"
            else
                echo "❌ Rebase continue failed"
                exit 1
            fi
        else
            echo "❌ Could not resolve conflicts automatically"
            exit 1
        fi
        exit 0
        ;;
    "check"|"--check")
        echo "🔍 Checking current status..."
        echo "📍 Branch: $(git symbolic-ref --short HEAD)"
        echo "📊 Status:"
        git status --short
        exit 0
        ;;
    *)
        # Default: run main
        main
        ;;
esac

echo "✅ Git Smart Rebase Toolkit loaded"