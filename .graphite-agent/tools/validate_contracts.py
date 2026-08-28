#!/usr/bin/env python3
"""Validate outputs against JSON contracts."""

import json
import sys
from pathlib import Path

AGENT_DIR = Path(".graphite-agent")
OUTPUTS_DIR = AGENT_DIR / "outputs"
CONTRACTS_DIR = AGENT_DIR / "contracts"


def load_contract(name):
    path = CONTRACTS_DIR / f"{name}.contract.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def validate_output(name, data):
    contract = load_contract(name)
    if not contract:
        return True, f"No contract for {name}"
    
    # Handle empty/minimal contracts (lists, empty dicts)
    if isinstance(contract, list):
        return True, f"{name}: contract is list schema, skipping type validation"
    if not isinstance(contract, dict):
        return True, f"{name}: contract is {type(contract).__name__}, skipping validation"
    
    # Minimal validation: check type constraints
    expected_type = contract.get("type")
    if expected_type == "object" and not isinstance(data, dict):
        return False, f"{name}: expected object, got {type(data).__name__}"
    if expected_type == "array" and not isinstance(data, list):
        return False, f"{name}: expected array, got {type(data).__name__}"
    
    # Check required properties if specified
    if "properties" in contract and isinstance(data, dict):
        for prop, schema in contract["properties"].items():
            if schema.get("required") and prop not in data:
                return False, f"{name}: missing required property {prop}"
    
    return True, f"{name}: valid"


def main():
    failures = []
    
    # Map output files to contract names
    checks = {
        "analysis_summary.json": "analysis_summary",
        "relationship_graph.json": "relationship_graph",
        "triage_packets.json": "triage_packets",
        "question_queue.json": "question_queue",
        "recommendations.json": "recommendations",
        "target_candidates.json": "target_candidates",
        "target_matrix.json": "target_matrix",
        "target_questions.json": "target_questions",
        "target_recommendations.json": "target_recommendations",
        "root_health.json": "root_health",
        "root_refresh_questions.json": "root_refresh_questions",
        "root_refresh_recommendations.json": "root_refresh_recommendations",
        "stack_order.json": "stack_order",
        "status_audit.json": "status_audit",
        "execution_plan.json": "execution_plan",
    }
    
    for output_file, contract_name in checks.items():
        output_path = OUTPUTS_DIR / output_file
        if not output_path.exists():
            continue
        
        try:
            data = json.loads(output_path.read_text())
            valid, msg = validate_output(contract_name, data)
            if not valid:
                failures.append(msg)
        except json.JSONDecodeError as e:
            failures.append(f"{output_file}: invalid JSON - {e}")
    
    if failures:
        print("Contract validation failed:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All output contracts validated successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
