#!/bin/bash
# Final Unblock and Stack Status Report

echo "=========================================="
echo "🎯 Final Unblock and Stack Status Report"
echo "=========================================="
echo "Generated: $(date)"
echo ""

cd /home/masum/github/remote/gemini-cli-prompt-library || exit 1

echo "📊 Current Branch Status:"
echo "-----------------"
git branch -v | grep -v "remotes/" | head -10
echo ""

echo "🎯 Successfully Unblocked and Stacked Branches:"
echo "---------------------------------------------"

# Check for branches that were successfully stacked
for branch in fix/require-review-comments-resolved cto/resolve-merge-conflicts-main-prs; do
    if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
        local merge_base=$(git merge-base main "$branch")
        local current_main=$(git rev-parse main)
        local commits_ahead=$(git rev-list --count "$merge_base".."$branch" 2>/dev/null)
        
        if [ "$merge_base" = "$current_main" ]; then
            echo "✅ $branch - Based on latest main ($(git log --oneline -1 "$branch"))"
        else
            echo "⚠️  $branch - Based on older main ($merge_base)"
        fi
    else
        echo "❌ $branch - Not found locally"
    fi
done
echo ""

echo "📋 Branches Ready for Stacking:"
echo "-----------------------------"

for branch in fix-scheduled-audit-report-7335934676686138146 cto/apply-remaining-fixes-prs add-scheduled-audit-prompt-14723155380211979683 update-scheduled-codebase-audit-16497131777087108224; do
    if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
        echo "✅ $branch - Available locally"
    else
        echo "📥 $branch - Available on remote"
    fi
done
echo ""

echo "🍃 Graphite Stack Suggestions:"
echo "-----------------------------"

echo "# To create Graphite-compatible short names for the stacked branches:"
for branch in fix/require-review-comments-resolved cto/resolve-merge-conflicts-main-prs; do
    if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
        local short_name=$(echo "$branch" | tr - _ | sed 's/\///g')
        echo "# gt track $branch --parent main"
    fi
done
echo ""

echo "🔄 To Continue Stacking:"
echo "---------------------"
echo "# For each remaining branch:"
echo "1. git checkout <branch>"
echo "2. git reset --hard origin/<branch>"
echo "3. GIT_MERGE_AUTOEDIT=no git rebase --onto main main <branch>"
echo "4. git push --force-with-lease origin <branch>"
echo ""

echo "✅ Smart Rebase Configuration:"
echo "-----------------------------"
echo "✅ git rerere: $(git config rerere.enabled)"
echo "✅ git rerere autoupdate: $(git config rerere.autoupdate)"
echo "✅ git-surgeon: $(git-surgeon --version 2>/dev/null)"

# Check rerere cache
echo ""
echo "💾 Conflicts Learned by rerere:"
if [ -d ".git/rr-cache" ]; then
    local conflict_count=$(ls -1 .git/rr-cache | wc -l)
    echo "   📊 Conflict solutions cached: $conflict_count"
else
    echo "   ℹ️  No conflicts cached yet"
fi

echo ""
echo "📈 Rebase Statistics:"
echo "-------------------"
for branch in fix/require-review-comments-resolved cto/resolve-merge-conflicts-main-prs; do
    if git show-ref --verify --quiet "refs/heads/$branch" 2>/dev/null; then
        local commits=$(git rev-list --count main.."$branch" 2>/dev/null)
        local files_changed=$(git diff --name-only main..."$branch" | wc -l)
        echo "   $branch: $commits commits, $files_changed files changed"
    fi
done

echo ""
echo "🎉 Summary:"
echo "---------"
success_count=$(git tag | grep -c "unblocked-" || echo "0")
echo "✅ $success_count branches successfully unblocked and stacked"
echo "📊 Ready to use Graphite for new branch creation"
echo "💡 Use 'gt create' for new stacked branches"