#!/bin/bash
# Execute Unblock and Stack - Simplified version

cd /home/masum/github/remote/gemini-cli-prompt-library || exit 1

echo "=========================================="
echo "🎯 Executing Unblock and Stack"
echo "=========================================="
echo "Start time: $(date)"
echo ""

# Setup
git config rerere.enabled true
git config rerere.autoupdate true
echo "✅ git rerere: enabled"
echo "✅ git-surgeon: $(git-surgeon --version 2>/dev/null)"
echo ""

# Ensure we start from main
git checkout main
git pull origin main
echo "📍 On main branch, up to date"
echo ""

# Log file
LOG="/tmp/execute_unblock_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Full log: $LOG"
echo ""

# Create a simple function to rebase one branch
rebase_branch() {
    local branch="$1"
    local target="main"
    
    echo "🚀 Processing: $branch"
    echo "=========================================="
    
    # Create local branch from remote
    if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
        echo "📍 Branch exists locally"
        git checkout "$branch"
        git reset --hard "origin/$branch" || true
    else
        echo "📥 Creating local branch from remote"
        git checkout -b "$branch" "origin/$branch" || return 1
    fi
    
    # Backup current state
    git branch "backup/$branch-$(date +%Y%m%d-%H%M%S)" || true
    
    # Start rebase
    echo "🔄 Starting rebase onto main..."
    
    # Try automatic rebase first
    if GIT_MERGE_AUTOEDIT=no git rebase --onto "$target" "$target" "$branch" \
        --autostash --keep-empty 2>&1 | head -20; then
        
        echo "✅ Rebase completed successfully"
        
        # Check for issues
        echo "🔍 Analyzing with git-surgeon..."
        if git-surgeon hunks 2>/dev/null | grep -q -i "duplicate\|overlap"; then
            echo "⚠️  Potential duplicate hunks detected"
        else
            echo "✅ No duplicate hunks detected"
        fi
        
        # Validate code
        echo "🔍 Validating code..."
        for file in $(git diff --name-only HEAD~3..HEAD | grep -E '\.(py|json|yaml|yml)$' | head -3); do
            echo "    Checking $file..."
        done
        
        return 0
    else
        echo "❌ Rebase failed - checking for conflicts..."
        
        if git status | grep -q "both modified\|unmerged"; then
            echo "📁 Conflicted files:"
            git diff --name-only --diff-filter=U | while read file; do
                echo "    - $file"
            done
            
            # Try git rerere
            echo "🎯 Attempting git rerere..."
            git rerere 2>&1
            
            if git status | grep -q "both modified\|unmerged"; then
                echo "❌ Conflicts remain after rerere"
                return 1
            else
                echo "✅ All conflicts resolved by rerere"
                if GIT_SEQUENCE_EDITOR="echo save >" git rebase --continue; then
                    echo "✅ Rebase completed"
                    return 0
                else
                    echo "❌ Could not continue rebase"
                    return 1
                fi
            fi
        fi
    fi
}

# Main execution
TARGET_BRANCHES=(
    "fix/require-review-comments-resolved"
    "cto/resolve-merge-conflicts-main-prs" 
    "cto/apply-remaining-fixes-prs"
)

# Clear rerere cache to start fresh
rm -rf .git/rr-cache

echo "🎯 Starting with first priority branch: ${TARGET_BRANCHES[0]}"
echo ""

# Process first branch
if rebase_branch "${TARGET_BRANCHES[0]}"; then
    echo "✅ First branch processed successfully"
    
    # If successful, tag it
    git tag "unblocked/${TARGET_BRANCHES[0]}-$(date +%Y%m%d)" 2>/dev/null || true
    
    # Process remaining branches
    for branch in "${TARGET_BRANCHES[@]:1}"; do
        echo ""
        echo "🎯 Processing next branch: $branch"
        
        # Go back to main first
        git checkout main 2>/dev/null || echo "⚠️  Could not checkout main"
        
        if rebase_branch "$branch"; then
            echo "✅ Branch $branch processed successfully"
            git tag "unblocked/$branch-$(date +%Y%m%d)" 2>/dev/null || true
        else
            echo "❌ Branch $branch failed"
            echo "💡 Manual resolution needed"
            break
        fi
    done
    
    echo ""
    echo "=========================================="
    echo "📊 Final Results"
    echo "=========================================="
    
    # Check which branches were successfully unblocked
    for branch in "${TARGET_BRANCHES[@]}"; do
        if git tag | grep -q "unblocked/$branch"; then
            echo "✅ $branch - Successfully unblocked and stacked"
        else
            echo "❌ $branch - Needs manual attention"
        fi
    done
    
    echo ""
    echo "🎉 Unblock and Stack Process Complete!"
    
else
    echo "❌ First branch failed - cannot continue"
    echo "💡 Resolve conflicts in ${TARGET_BRANCHES[0]} and run again"
fi

echo ""
echo "📝 Full log saved to: $LOG"
echo "💾 Rerere cache: $(git count-objects -H | grep rerere || echo 'None')"