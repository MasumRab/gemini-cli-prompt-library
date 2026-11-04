#!/bin/bash
# Quick stack the remaining branches using trained git rerere

cd /home/masum/github/remote/gemini-cli-prompt-library || exit 1

echo "=========================================="
echo "🚀 Quick Stack Remaining Branches"
echo "=========================================="
echo "Using trained git rerere for faster conflict resolution"
echo ""

# Remaining branches to stack
BRANCHES=(
    "cto/apply-remaining-fixes-prs"
    "fix-scheduled-audit-report-7335934676686138146" 
    "add-scheduled-audit-prompt-14723155380211979683"
    "update-scheduled-codebase-audit-16497131777087108224"
)

echo "🎯 Branches to process: ${#BRANCHES[@]}"
for branch in "${BRANCHES[@]}"; do
    echo "   - $branch"
done
echo ""

success=0
failed=0
total=${#BRANCHES[@]}

# Ensure we start from clean main
git checkout main

for branch in "${BRANCHES[@]}"; do
    echo ""
    echo "🎯 Processing branch $(($success + $failed + 1))/$total: $branch"
    
    if ! git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
        echo "ℹ️  Creating local branch from remote..."
        git checkout -b "$branch" "origin/$branch" 2>/dev/null || { echo "❌ Failed to create $branch"; ((failed++)); continue; }
    else
        echo "ℹ️  Using existing local branch..."
        git checkout "$branch" 2>/dev/null || { echo "❌ Failed to checkout $branch"; ((failed++)); continue; }
        git reset --hard "origin/$branch" 2>/dev/null || true
    fi
    
    echo "🔄 Starting rebase (with trained rerere)..."
    
    # Try automatic rebase
    if GIT_MERGE_AUTOEDIT=no git rebase --onto main main "$branch" --autostash --keep-empty 2>&1; then
        echo "✅ Successfully stacked: $branch"
        ((success++))
        git tag "stacked/$branch-$(date +%Y%m%d)" 2>/dev/null || true
    else
        echo "⚠️  Rebase failed for $branch"
        
        # Check for conflicts
        if git status | grep -q "both modified\|unmerged"; then
            echo "📁 Conflicts found, trying rerere..."
            
            # Record conflicts first
            git rerere 2>/dev/null
            
            # If rerere can resolve, it will
            if git status | grep -q "both modified\|unmerged"; then
                # Try to accept both sides
                for file in $(git diff --name-only --diff-filter=U); do
                    git checkout --theirs "$file" 2>/dev/null && git add "$file"
                    echo "    ✅ Accepted theirs for $file"
                done
                
                if ! git status | grep -q "both modified\|unmerged"; then
                    echo "✅ All conflicts resolved"
                    if GIT_SEQUENCE_EDITOR="echo 'auto-merge' >" git rebase --continue 2>/dev/null; then
                        echo "✅ Successfully continued: $branch"
                        ((success++))
                        git tag "stacked/$branch-$(date +%Y%m%d)" 2>/dev/null || true
                    else
                        echo "❌ Could not continue rebase for $branch"
                        ((failed++))
                    fi
                else
                    echo "❌ Conflicts remain for $branch"
                    ((failed++))
                fi
            fi
        else
            echo "❌ Rebase failed for unknown reasons"
            ((failed++))
        fi
    fi
    
    # Return to main for next iteration
    git checkout main 2>/dev/null || true
    
done

echo ""
echo "=========================================="
echo "📊 Final Results"
echo "=========================================="
echo "✅ Successfully stacked: $success/$total"
echo "❌ Failed: $failed/$total"

if [ $failed -eq 0 ]; then
    echo ""
    echo "🎉 All remaining branches stacked successfully!"
    echo ""
    echo "🎯 New Stack:"
    for branch in "${BRANCHES[@]}"; do
        echo "   ✅ $branch"
    done
else
    echo ""
    echo "⚠️  $failed branches need manual attention"
fi

echo ""
echo "💾 Rerere cache trained on: $(ls .git/rr-cache 2>/dev/null | wc -l) conflict patterns"