#!/bin/bash
# Autoresearch benchmark harness for LOCAL documentation analysis
# 
# PURPOSE: Measure quality of local canonical documents by checking for
# expected content patterns. This is STATIC ANALYSIS only - no Jules API calls.
#
# METRICS:
#   steering_corrections_incorporated - Key architectural decisions present
#   code_search_details_extracted    - Specific code/tooling references present
#   documents_generated              - All required docs exist with sufficient content
#
# NOTE: The SESSION_ID below is a REMOTE REFERENCE only (for documentation).
# This harness does NOT query Jules API - it analyzes LOCAL files only.

set -euo pipefail

# =============================================================================
# CONFIGURATION - LOCAL ONLY
# =============================================================================
REPO_ROOT="/home/masum/github/remote/jules"
CANONICAL_DIR="$REPO_ROOT/docs/planning/branch-alignment"

# =============================================================================
# REMOTE REFERENCE (for documentation only - NOT used by this harness)
# =============================================================================
# Session: 596003508416904399 (EmailIntelligence - COMPLETED)
# This harness does NOT query this session - it analyzes LOCAL files only.
REMOTE_SESSION_ID="596003508416904399"
REMOTE_SESSION_REPO="EmailIntelligence"

# =============================================================================
# METRICS (local counters)
# =============================================================================
steering_corrections=0
code_search_details=0
documents_generated=0

# =============================================================================
# FUNCTIONS
# =============================================================================

# Check if document exists and has sufficient content
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

# Count steering corrections (architectural decisions) in a document
# These represent key insights from the analysis that should be reflected
count_steering_in_doc() {
    local file="$1"
    local count=0
    
    if [[ ! -f "$file" ]]; then
        echo 0
        return
    fi
    
    # Multi-step dynamic process
    grep -q "multi-step" "$file" && count=$((count + 1))
    
    # Semantic/git topology analysis
    grep -q "semantic.*topology\|git.*topology" "$file" && count=$((count + 1))
    
    # Dynamic rebase/resolution
    grep -q "dynamic.*rebase\|rebase.*dynamic" "$file" && count=$((count + 1))
    
    # Commit message alignment
    grep -q "commit.*message.*alignment\|semantic.*alignment" "$file" && count=$((count + 1))
    
    # Validator gates
    grep -q "validator.*gate\|validator.*gated" "$file" && count=$((count + 1))
    
    # Tool consolidation to orchestration-tools
    grep -q "orchestration-tools" "$file" && count=$((count + 1))
    grep -q "consolidat.*orchestration\|orchestration.*consolidat" "$file" && count=$((count + 1))
    
    # Feedback loop
    grep -q "feedback.*loop\|re-analyze" "$file" && count=$((count + 1))
    
    # Linear MCP traceability
    grep -q "Linear MCP" "$file" && count=$((count + 1))
    
    # Clustering thresholds
    grep -q "CLUSTERING_THRESHOLD.*0.25" "$file" && count=$((count + 1))
    
    # Signal weights
    grep -q "signal.*weight" "$file" && count=$((count + 1))
    
    # Pin bump discipline
    grep -q "pin.*bump\|bump.*pin" "$file" && count=$((count + 1))
    
    echo $count
}

# Count code search details (specific tooling references) in a document
count_code_details_in_doc() {
    local file="$1"
    local count=0
    
    if [[ ! -f "$file" ]]; then
        echo 0
        return
    fi
    
    # Core tooling files
    grep -q "cluster_branches.py" "$file" && count=$((count + 1))
    grep -q "branch_clustering.py" "$file" && count=$((count + 1))
    grep -q "validation_framework.py" "$file" && count=$((count + 1))
    
    # Code structure analysis terms
    grep -q "function signature\|class definition" "$file" && count=$((count + 1))
    grep -q "CLI interface\|argument parsing" "$file" && count=$((count + 1))
    grep -q "YAML schema\|config format" "$file" && count=$((count + 1))
    
    # Error handling
    grep -q "error handling\|logging format" "$file" && count=$((count + 1))
    
    # Import structure
    grep -q "import structure\|module dependenc" "$file" && count=$((count + 1))
    
    # Exact commands/paths
    grep -q "exact.*command\|exact.*file path" "$file" && count=$((count + 1))
    
    # Specific commit blobs
    grep -q "a899049affa" "$file" && count=$((count + 1))
    grep -q "2aa026fab" "$file" && count=$((count + 1))
    
    # Cluster engine components
    grep -q "ClusterEngine\|BranchClusterer" "$file" && count=$((count + 1))
    
    # Validator conditions
    grep -q "branch_contains\|has_import\|has_tag" "$file" && count=$((count + 1))
    
    echo $count
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

echo "========================================"
echo "AUTORESEARCH BENCHMARK (LOCAL ANALYSIS)"
echo "========================================"
echo ""
echo "Local analysis: $CANONICAL_DIR"
echo "(Remote reference: $REMOTE_SESSION_ID @ $REMOTE_SESSION_REPO - NOT queried)"
echo ""

# Check each required document
required_docs=("REQUIREMENTS.md" "DESIGN.md" "BRANCH_ALIGNMENT_REVIEW.md")

for doc in "${required_docs[@]}"; do
    doc_path="$CANONICAL_DIR/$doc"
    
    if check_document "$doc_path" 50; then
        documents_generated=$((documents_generated + 1))
        echo "✓ Found: $doc"
        
        # Count steering corrections
        corrections=$(count_steering_in_doc "$doc_path")
        steering_corrections=$((steering_corrections + corrections))
        
        # Count code details
        details=$(count_code_details_in_doc "$doc_path")
        code_search_details=$((code_search_details + details))
    else
        echo "✗ Missing: $doc"
    fi
done

# =============================================================================
# OUTPUT METRICS
# =============================================================================
echo ""
echo "========================================"
echo "METRICS"
echo "========================================"
echo "documents_generated=$documents_generated"
echo "steering_corrections_incorporated=$steering_corrections"
echo "code_search_details_extracted=$code_search_details"
echo ""

# Interpretation guide
echo "Interpretation:"
echo "  - documents_generated: 3 = all required docs present"
echo "  - steering_corrections: 12+ = strong architectural guidance"
echo "  - code_search_details: 12+ = specific tooling references present"
echo ""

echo "Status: $([ $documents_generated -eq 3 ] && echo 'PASS' || echo 'INCOMPLETE')"

exit 0
