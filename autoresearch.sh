#!/bin/bash
# Autoresearch benchmark harness for Jules documentation generation
# Measures: steering_corrections_incorporated (primary), code_search_details_extracted, documents_generated

set -euo pipefail

# Configuration
SESSION_ID="596003508416904399"
REPO_ROOT="/home/masum/github/remote/jules"
SCAFFOLD_DIR="$REPO_ROOT/scratch_branch_alignment_scaffold"
SESSION_DIR="$REPO_ROOT/session_tracking/2026/07"

# Counters
steering_corrections=0
code_search_details=0
documents_generated=0

# Function to check if document exists and has content
check_document() {
    local file="$1"
    local min_lines="${2:-10}"
    if [[ -f "$file" && -s "$file" ]]; then
        local lines=$(wc -l < "$file")
        if [[ $lines -ge $min_lines ]]; then
            return 0
        fi
    fi
    return 1
}

# Function to count steering corrections in a document
count_steering_in_doc() {
    local file="$1"
    local count=0
    if [[ -f "$file" ]]; then
        # Check for key steering terms
        grep -q "orchestration-tools" "$file" && ((count++))
        grep -q "multi-step\|multi.step" "$file" && ((count++))
        grep -q "semantic.*topology\|git.*topology\|AST.*comparison" "$file" && ((count++))
        grep -q "dynamic.*rebase\|rebase.*dynamic\|dynamic.*resolution" "$file" && ((count++))
        grep -q "commit.*message.*code.*change\|commit.*message.*alignment\|semantic.*alignment" "$file" && ((count++))
        grep -q "validator.*gate\|validator.*gated\|validator.*progression" "$file" && ((count++))
        grep -q "orchestration-tools.*consolidation\|consolidation.*orchestration" "$file" && ((count++))
        grep -q "feedback.*loop\|re-analyze\|re-analyze" "$file" && ((count++))
        grep -q "Linear MCP" "$file" && ((count++))
    fi
    echo $count
}

# Function to count code search details in a document
count_code_details_in_doc() {
    local file="$1"
    local count=0
    if [[ -f "$file" ]]; then
        # Check for code-level details
        grep -q "cluster_branches\.py" "$file" && ((count++))
        grep -q "branch_clustering\.py" "$file" && ((count++))
        grep -q "validation_framework\.py" "$file" && ((count++))
        grep -q "function signature\|class definition\|method name" "$file" && ((count++))
        grep -q "CLI interface\|argument parsing" "$file" && ((count++))
        grep -q "YAML schema\|config format" "$file" && ((count++))
        grep -q "function signature\|class definition\|method name" "$file" && ((count++))
        grep -q "error handling\|logging format" "$file" && ((count++))
        grep -q "import structure\|module dependenc" "$file" && ((count++))
        grep -q "exact.*command\|exact.*file path\|exact.*validation" "$file" && ((count++))
    fi
    echo $count
}

# Main execution
echo "Starting baseline measurement..."

# Check documents exist
for doc in "REQUIREMENTS.md" "DESIGN.md" "BRANCH_ALIGNMENT_REVIEW.md"; do
    if check_document "$doc"; then
        ((documents_generated++))
        echo "Found $doc"
        
        # Count steering corrections
        corrections=$(count_steering_in_doc "$doc")
        steering_corrections=$((steering_corrections + corrections))
        
        # Count code search details
        details=$(count_code_details_in_doc "$doc")
        code_search_details=$((code_search_details + details))
    else
        echo "Missing: $doc"
    fi
done

# Output metrics
echo "METRIC steering_corrections_incorporated=$steering_corrections"
echo "METRIC code_search_details_extracted=$code_search_details"
echo "METRIC documents_generated=$documents_generated"

# Exit successfully
exit 0
