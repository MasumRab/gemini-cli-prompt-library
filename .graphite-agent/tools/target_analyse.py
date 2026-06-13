#!/usr/bin/env python3
"""Analyse target intent for each branch."""
import argparse
import json
from pathlib import Path
from agent_core import OUTPUTS_DIR, ensure_dirs, write_json, read_json, load_snapshot, branch_nodes

def build_target_matrix(snapshot):
    """Build target matrix mapping branches to candidate targets."""
    nodes = branch_nodes(snapshot)
    matrix = {'branches': {}}
    for branch, node in nodes.items():
        declared = node.get('declared_base')
        resolved = node.get('resolved_parent')
        root = node.get('root_branch')
        matrix['branches'][branch] = {
            'declared_target': declared,
            'candidate_targets': [{'target': resolved, 'confidence': 'high' if node.get('status') in {'safe', 'needs_restack'} else 'medium'}] if resolved else [],
            'confirmed_targets': [root] if root else [],
            'requires_user_decision': node.get('status') not in {'safe', 'needs_restack'}
        }
    return matrix

if __name__ == '__main__':
    ensure_dirs()
    snapshot = load_snapshot()
    matrix = build_target_matrix(snapshot)
    write_json(OUTPUTS_DIR / 'target_matrix.json', matrix)
    print(json.dumps(matrix, indent=2))
