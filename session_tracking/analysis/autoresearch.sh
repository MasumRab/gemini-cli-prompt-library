#!/bin/bash
# Autoresearch benchmark harness for Jules documentation generation
# Measures: steering_corrections_incorporated, code_search_details_extracted, documents_generated

# Configuration
SESSION_ID="596003508416904399"
REPO_ROOT="/home/masum/github/remote/jules"
CANONICAL_DIR="$REPO_ROOT/docs/planning/branch-alignment"

# Counters
steering_corrections=0
code_search_details=0
documents_generated=0

# Function to check if document exists and has content
check_document() {
	local file="$1"
	local min_lines="${2:-10}"
	if [[ -f "$file" ]] && [[ -s "$file" ]]; then
		local lines=$(wc -l <"$file")
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
		grep -q "orchestration-tools" "$file" && count=$((count + 1))
		grep -q "multi-step" "$file" && count=$((count + 1))
		grep -q "semantic.*topology" "$file" && count=$((count + 1))
		grep -q "dynamic.*rebase" "$file" && count=$((count + 1))
		grep -q "commit.*message.*alignment" "$file" && count=$((count + 1))
		grep -q "validator.*gate" "$file" && count=$((count + 1))
		grep -q "consolidation.*orchestration" "$file" && count=$((count + 1))
		grep -q "feedback.*loop" "$file" && count=$((count + 1))
		grep -q "Linear MCP" "$file" && count=$((count + 1))
		grep -q "CLUSTERING_THRESHOLD.*0.25" "$file" && count=$((count + 1))
		grep -q "signal.*weight" "$file" && count=$((count + 1))
		grep -q "pin.bump" "$file" && count=$((count + 1))
	fi
	echo $count
}

# Function to count code search details in a document
count_code_details_in_doc() {
	local file="$1"
	local count=0
	if [[ -f "$file" ]]; then
		grep -q "cluster_branches.py" "$file" && count=$((count + 1))
		grep -q "branch_clustering.py" "$file" && count=$((count + 1))
		grep -q "validation_framework.py" "$file" && count=$((count + 1))
		grep -q "function signature" "$file" && count=$((count + 1))
		grep -q "CLI interface" "$file" && count=$((count + 1))
		grep -q "YAML schema" "$file" && count=$((count + 1))
		grep -q "error handling" "$file" && count=$((count + 1))
		grep -q "import structure" "$file" && count=$((count + 1))
		grep -q "exact.*command" "$file" && count=$((count + 1))
		grep -q "a899049affa" "$file" && count=$((count + 1))
		grep -q "ClusterEngine" "$file" && count=$((count + 1))
		grep -q "branch_contains" "$file" && count=$((count + 1))
	fi
	echo $count
}

# Main execution
echo "Starting autoresearch benchmark..."
echo "Session: $SESSION_ID"
echo "Canonical dir: $CANONICAL_DIR"
echo ""

# Check canonical documents exist
for doc in "REQUIREMENTS.md" "DESIGN.md" "BRANCH_ALIGNMENT_REVIEW.md"; do
	if check_document "$CANONICAL_DIR/$doc"; then
		documents_generated=$((documents_generated + 1))
		echo "Found canonical $doc"
		corrections=$(count_steering_in_doc "$CANONICAL_DIR/$doc")
		steering_corrections=$((steering_corrections + corrections))
		details=$(count_code_details_in_doc "$CANONICAL_DIR/$doc")
		code_search_details=$((code_search_details + details))
	else
		echo "Missing canonical: $doc"
	fi
done

# Output metrics
echo ""
echo "=== METRICS ==="
echo "METRIC steering_corrections_incorporated=$steering_corrections"
echo "METRIC code_search_details_extracted=$code_search_details"
echo "METRIC documents_generated=$documents_generated"

exit 0
