#!/bin/bash
# Autoresearch benchmark harness for EmailIntelligence branch alignment docs
#
# PURPOSE: Measure quality of local canonical documents by checking for
# expected content patterns. This is STATIC ANALYSIS only - no Jules API calls.
#
# METRICS:
#   steering_corrections_incorporated - Key architectural decisions present
#   code_search_details_extracted    - Specific code/tooling references present
#   documents_generated              - All required docs exist with sufficient content

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANONICAL_DIR="$WORKSPACE_DIR/analysis/branch-alignment"

# =============================================================================
# SESSION REFERENCE (for documentation only)
# =============================================================================
REMOTE_SESSION_ID="596003508416904399"
REMOTE_SESSION_REPO="EmailIntelligence"

# =============================================================================
# METRICS
# =============================================================================
steering_corrections=0
code_search_details=0
documents_generated=0

# =============================================================================
# FUNCTIONS
# =============================================================================

check_document() {
    local file="$1"
    local min_lines="${2:-50}"
    
    if [[ -f "$file" ]] && [[ -s "$file" ]]; then
        local lines=$(wc -l <"$file")
        if [[ $lines -ge $min_lines ]]; then
            return 0
        fi
    fi
    return 1
}

count_steering_in_doc() {
    local file="$1"
    local count=0
    
    [[ ! -f "$file" ]] && echo 0 && return
    
    grep -q "orchestration-tools" "$file" && count=$((count + 1))
    grep -q "multi-step" "$file" && count=$((count + 1))
    grep -q "semantic.*topology\|git.*topology" "$file" && count=$((count + 1))
    grep -q "dynamic.*rebase\|rebase.*dynamic" "$file" && count=$((count + 1))
    grep -q "commit.*message.*alignment" "$file" && count=$((count + 1))
    grep -q "validator.*gate" "$file" && count=$((count + 1))
    grep -q "consolidat.*orchestration\|orchestration.*consolidat" "$file" && count=$((count + 1))
    grep -q "feedback.*loop\|re-analyze" "$file" && count=$((count + 1))
    grep -q "Linear MCP" "$file" && count=$((count + 1))
    grep -q "CLUSTERING_THRESHOLD.*0.25" "$file" && count=$((count + 1))
    grep -q "signal.*weight" "$file" && count=$((count + 1))
    grep -q "pin.*bump\|bump.*pin" "$file" && count=$((count + 1))
    
    echo $count
}

count_code_details_in_doc() {
    local file="$1"
    local count=0
    
    [[ ! -f "$file" ]] && echo 0 && return
    
    grep -q "cluster_branches.py" "$file" && count=$((count + 1))
    grep -q "branch_clustering.py" "$file" && count=$((count + 1))
    grep -q "validation_framework.py" "$file" && count=$((count + 1))
    grep -q "function signature\|class definition" "$file" && count=$((count + 1))
    grep -q "CLI interface\|argument parsing" "$file" && count=$((count + 1))
    grep -q "YAML schema\|config format" "$file" && count=$((count + 1))
    grep -q "error handling\|logging format" "$file" && count=$((count + 1))
    grep -q "import structure\|module dependenc" "$file" && count=$((count + 1))
    grep -q "exact.*command\|exact.*file path" "$file" && count=$((count + 1))
    grep -q "a899049affa" "$file" && count=$((count + 1))
    grep -q "2aa026fab" "$file" && count=$((count + 1))
    grep -q "ClusterEngine\|BranchClusterer" "$file" && count=$((count + 1))
    grep -q "branch_contains\|has_import\|has_tag" "$file" && count=$((count + 1))
    
    echo $count
}

# =============================================================================
# MAIN
# =============================================================================

echo "========================================"
echo "EMAILINTELLIGENCE BRANCH ALIGNMENT BENCHMARK"
echo "========================================"
echo ""
echo "Workspace: $WORKSPACE_DIR"
echo "Canonical docs: $CANONICAL_DIR"
echo "Session: $REMOTE_SESSION_ID @ $REMOTE_SESSION_REPO"
echo ""

for doc in "REQUIREMENTS.md" "DESIGN.md" "BRANCH_ALIGNMENT_REVIEW.md"; do
    doc_path="$CANONICAL_DIR/$doc"
    
    if check_document "$doc_path" 50; then
        documents_generated=$((documents_generated + 1))
        echo "✓ Found: $doc"
        corrections=$(count_steering_in_doc "$doc_path")
        steering_corrections=$((steering_corrections + corrections))
        details=$(count_code_details_in_doc "$doc_path")
        code_search_details=$((code_search_details + details))
    else
        echo "✗ Missing: $doc"
    fi
done

echo ""
echo "========================================"
echo "METRICS"
echo "========================================"
echo "documents_generated=$documents_generated"
echo "steering_corrections_incorporated=$steering_corrections"
echo "code_search_details_extracted=$code_search_details"
echo ""
echo "Status: $([ $documents_generated -eq 3 ] && echo 'PASS' || echo 'INCOMPLETE')"

exit 0
