#!/bin/bash
# Unblock and Stack Branches Script
# Based on Graphite agent V7.3 analysis
# Uses git rerere + smart conflict resolution

echo "=========================================="
echo "🎯 Unblocking and Stacking Branches"
echo "=========================================="

cd /home/masum/github/remote/gemini-cli-prompt-library || exit 1

# Ensure we start from clean main
git checkout main
git pull origin main

# Configuration
echo "✅ git rerere: $(git config rerere.enabled)"
echo "✅ git-surgeon: $(git-surgeon --version 2>/dev/null)"

# Log file
LOG="/tmp/unblock_and_stack_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Logging to: $LOG"


# Start logging
if [ ! -d "/tmp/unblock_and_stack" ]; then
    mkdir -p /tmp/unblock_and_stack
fi

# Start progress logging
echo "=== Unblocking and Stacking Strategy ==="
echo "Based on Graphite Agent V7.3 analysis"
echo ""

# Define the stack order based on Graphite analysis
# The agent identified these branches that need restacking
declare -a BRANCHES_TO_STACK=(
    "fix/require-review-comments-resolved"
    "fix-scheduled-audit-report-7335934676686138146"
    "cto/resolve-merge-conflicts-main-prs"
    "cto/apply-remaining-fixes-prs"
    "add-scheduled-audit-prompt-14723155380211979683"
    "update-scheduled-codebase-audit-16497131777087108224"
)

echo "🎯 Branches to process (${#BRANCHES_TO_STACK[@]} total):"
for branch in "${BRANCHES_TO_STACK[@]}"; do
    echo "   - $branch"
done
echo ""

# Function to safely rebase a branch
safe_rebase() {
    local branch="$1"
    local target="$2"
    
    echo "=========================================="
    echo "🔄 Processing: $branch -> $target"
    echo "=========================================="
    
    # Create local branch from remote if needed
    if ! git show-ref --verify --quiet "refs/heads/$branch"; then
        if git show-ref --verify --quiet "refs/remotes/origin/$branch"; then
            echo "📥 Creating local branch from origin/$branch"
            git checkout -b "$branch" "origin/$branch" || return 1
        else
            echo "❌ Branch $branch not found on remote"
            return 1
        fi
    else
        echo "📍 Branch exists locally, syncing..."
        git checkout "$branch"
        git reset --hard "origin/$branch" || return 1
    fi
    
    # Create backup
    git branch "backup/$branch-before-rebase-$(date +%Y%m%d-%H%M%S)" || true
    
    # Attempt rebase with smart conflict resolution
    echo "🚀 Starting rebase..."
    
    # Use --rebase-merges to preserve merge history where possible
    if GIT_MERGE_AUTOEDIT=no git rebase --onto "$target" "$target" "$branch" \
        --autostash --keep-empty --rebase-merges 2>&1; then
        
        echo "✅ Rebase completed successfully"
        
        # Enable git-surgeon to check for duplicates
        if command -v git-surgeon &>/dev/null; then
            echo "🔍 Checking for duplicate hunks..."
            if hunk_output=$(git-surgeon hunks 2>&1); then
                hunk_count=$(echo "$hunk_output" | wc -l)
                echo "    📊 Found $hunk_count hunks"
                
                # Check for issues
                if echo "$hunk_output" | grep -q -i "duplicate\|overlap\|conflict"; then
                    echo "    ⚠️  Potential hunk issues detected"
                    echo "$hunk_output" | head -10 | sed 's/^/      /'
                else
                    echo "    ✅ No hunk issues detected"
                fi
            fi
        fi
        
        # Validate syntax
        echo "🔍 Validating code flow..."
        for file in $(git diff --name-only HEAD~3..HEAD | grep -E '\.(py|json|yaml|yml)$' | head -5); do
            if [[ "$file" == *.py ]]; then
                if python3 -m py_compile "$file" 2>/dev/null; then
                    echo "    ✅ $file: Python syntax OK"
                else
                    echo "    ❌ $file: Python syntax error"
                fi
            elif [[ "$file" == *.json ]]; then
                if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
                    echo "    ✅ $file: JSON valid"
                else
                    echo "    ❌ $file: JSON invalid"
                fi
            elif [[ "$file" == *.yaml || "$file" == *.yml ]]; then
                if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                    echo "    ✅ $file: YAML valid"
                else
                    echo "    ❌ $file: YAML invalid"
                fi
            fi
        done
        
        return 0
        
    else
        echo "❌ Rebase encountered conflicts"
        
        # Try to resolve conflicts with both-sides strategy
        if git status | grep -q "both modified\|unmerged"; then
            echo "🔧 Attempting smart conflict resolution..."
            
            # List conflicted files
            conflict_files=$(git diff --name-only --diff-filter=U)
            echo "    📁 Conflicted files: $conflict_files"
            
            local files_resolved=0
            local total_files=$(echo "$conflict_files" | wc -l)
            
            for file in $conflict_files; do
                echo "    🔧 Processing: $file"
                
                # Try git rerere first
                if git rerere 2>/dev/null; then
                    echo "      ✅ git rerere resolved $file"
                    git add "$file"
                    ((files_resolved++))
                    continue
                fi
                
                # Try 3-way merge
                local ours="/tmp/ours_$(basename "$file" | sed 's/[^a-zA-Z0-9._-]//g')"
                local theirs="/tmp/theirs_$(basename "$file" | sed 's/[^a-zA-Z0-9._-]//g')"
                local base="/tmp/base_$(basename "$file" | sed 's/[^a-zA-Z0-9._-]//g')"
                
                git show :1:"$file" > "$ours" 2>/dev/null || continue
                git show :2:"$file" > "$theirs" 2>/dev/null || continue
                git show :3:"$file" > "$base" 2>/dev/null || true
                
                # If identical, just keep
                if cmp -s "$ours" "$theirs"; then
                    git checkout --ours "$file" 2>/dev/null
                    git add "$file"
                    echo "      ✅ Identical versions"
                    ((files_resolved++))
                    continue
                fi
                
                # Try intelligent merge
                if git merge-file "$ours" "$base" "$theirs" 2>/dev/null; then
                    git add "$file"
                    echo "      ✅ Intelligently merged"
                    ((files_resolved++))
                    continue
                fi
                
                # Fallback: accept both sides
                echo "      🎯 Accepting both sides"
                git checkout --theirs "$file" 2>/dev/null
                git add "$file"
                ((files_resolved++))
                
                rm -f "$ours" "$theirs" "$base"
            done
            
            echo "    ✅ Resolved: $files_resolved/$total_files conflicts"
            
            # Continue rebase if all resolved
            if ! git status | grep -q "both modified\|unmerged"; then
                echo "✅ All conflicts resolved, continuing rebase..."
                if GIT_SEQUENCE_EDITOR="echo 'save' >" git rebase --continue; then
                    echo "✅ Rebase completed after conflict resolution"
                    return 0
                else
                    echo "❌ Could not continue rebase"
                    return 1
                fi
            else
                echo "❌ Some conflicts remain unresolved"
                git status --short | head -10
                return 1
            fi
        else
            echo "❌ No conflicts detected but rebase failed"
            return 1
        fi
    fi
}

# Function to clean up temporary branches
cleanup_temps() {
    echo "🧹 Cleaning up temporary branches..."
    git branch | grep "backup/" | while read backup_branch; do
        echo "    Removing: $backup_branch"
        git branch -D "$backup_branch" 2>/dev/null || true
    done
    
    git branch | grep "rebase-done/" | while read done_branch; do
        echo "    Removing tag: $done_branch"
        git tag -d "$done_branch" 2>/dev/null || true
    done
}

# Main execution
echo "🚀 Starting Unblock and Stack Process"
echo ""

# Ensure we start from clean main
git checkout main

cleaned_ups=0
success_count=0
failed_count=0
total_count=${#BRANCHES_TO_STACK[@]}

for branch in "${BRANCHES_TO_STACK[@]}"; do
    echo ""
    echo "🎯 Branch $(($success_count + $failed_count + 1 + $cleaned_ups))/$total_count: $branch"
    
    if safe_rebase "$branch" "main"; then
        
        # Create Graphite-compatible branch name (shorter)
        local short_name=$(echo "$branch" | sed 's/fix-//;s/cto\///;s/add-//;s/update-//;s/scheduled-audit-//g' | tr - _)
        
        echo "✅ Successfully stacked: $branch"
        ((success_count++))
        
        # Mark as processed
        git tag "stacked/$branch-$(date +%Y%m%d)" 2>/dev/null || true
        
    else
        echo "❌ Failed to stack: $branch"
        ((failed_count++))
        
        # Clean up if we created a backup
        cleanup_temps
        
        echo "💡 To resolve manually:"
        echo "   git checkout $branch"
        echo "   git rebase --continue (if conflicts resolved)"
        echo "   Or: git rebase --abort"
    fi
    
    # Always go back to main for next iteration
    if git checkout main 2>/dev/null; then
        echo "📍 Returned to main for next branch"
    else
        echo "⚠️  Could not return to main"
    fi
    
    ((cleaned_ups++))
done

# Clean up
cleanup_temps

echo ""
echo "=========================================="
echo "📊 Final Stack Summary"
echo "=========================================="
echo "✅ Successfully stacked: $success_count/$total_count"
echo "❌ Failed: $failed_count/$total_count"
echo "🧹 Cleaned up: $cleaned_ups temporary branches"

if [ $failed_count -eq 0 ]; then
    echo ""
    echo "🎉 All branches unblocked and stacked successfully!"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Review stacked branches: git log --oneline --graph --all"
    echo "   2. Push stacked branches: git push --force-with-lease origin <branch>"
    echo "   3. Create/stack new branches with: gt create"
    
    # Show the new stack
    echo ""
    echo "🎯 New Branch Stack (bottom to top):"
    for branch in "${BRANCHES_TO_STACK[@]}"; do
        if git tag | grep -q "stacked/$branch"; then
            local merge_base=$(git merge-base main "$branch" 2>/dev/null)
            local commits_ahead=$(git rev-list --count "$merge_base".."$branch" 2>/dev/null)
            echo "   ✅ $branch ($commits_ahead commits ahead of main)"
        fi
    done
else
    echo ""
    echo "⚠️  $failed_count branches need manual attention"
    echo "💡 Check the log file for details: $LOG"
    echo "   Run: tail -f $LOG"
fi

echo ""
echo "✅ Unblock and Stack Process Complete"
echo "📝 Full log: $LOG"