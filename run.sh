#!/bin/bash
# DSPy-HELM Batch Runner
# Runs multiple scenarios with sequential provider failover
# ALL PROVIDERS USE FREE TIER - TOTAL COST: $0

set -e

# Configuration
SCENARIOS=("security_review" "unit_test" "documentation" "api_design")
OPTIMIZERS=("MIPROv2" "BootstrapFewShot")
PROVIDER="auto"  # auto uses failover chain
MODEL="auto"
OUTPUT_DIR="agents"
PARALLEL=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "DSPy-HELM Batch Runner"
echo "Total Cost: \$0 (all free tier)"
echo "========================================"
echo "Scenarios: ${SCENARIOS[*]}"
echo "Optimizers: ${OPTIMIZERS[*]}"
echo "Provider: $PROVIDER (auto = failover chain)"
echo "Output: $OUTPUT_DIR"
echo "========================================"
echo ""

run_scenario() {
    local scenario=$1
    local optimizer=$2
    
    echo -e "${YELLOW}Running: $scenario with $optimizer${NC}"
    
    python -m dspy_helm.cli \
        --scenario "$scenario" \
        --optimizer "$optimizer" \
        --provider "$PROVIDER" \
        --model "$MODEL" \
        --output "$OUTPUT_DIR"
    
    echo -e "${GREEN}Completed: $scenario with $optimizer${NC}"
    echo ""
}

if [ "$PARALLEL" = true ]; then
    for scenario in "${SCENARIOS[@]}"; do
        for optimizer in "${OPTIMIZERS[@]}"; do
            run_scenario "$scenario" "$optimizer" &
            PIDS+=($!)
        done
    done
    
    for pid in "${PIDS[@]}"; do
        wait $pid || exit 1
    done
else
    for scenario in "${SCENARIOS[@]}"; do
        for optimizer in "${OPTIMIZERS[@]}"; do
            run_scenario "$scenario" "$optimizer"
        done
    done
fi

echo "========================================"
echo -e "${GREEN}All runs completed successfully!${NC}"
echo "Total Cost: \$0 (all providers use free tier)"
echo "========================================"
