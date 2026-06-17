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
        status = node.get('status')
        audit = node.get('audit', {})
        merge = audit.get('merge_analysis', {})
        diag_cat = None
        if status == 'blocked_merge_commits' and merge.get('trunk_updates'):
            diag_cat = 'in_target_conflict_resolution_merge'
        elif status == 'cross_root_conflict':
            diag_cat = 'cross_root_contamination'
        elif status == 'manual_triage':
            diag_cat = 'target_intent_required'
        matrix['branches'][branch] = {
            'declared_target': declared,
            'candidate_targets': [{'target': resolved, 'confidence': 'high' if status in {'safe', 'needs_restack'} else 'medium'}] if resolved else [],
            'confirmed_targets': [root] if root else [],
            'diagnostic_category': diag_cat,
            'requires_user_decision': status not in {'safe', 'needs_restack'}
        }
    return matrix

if __name__ == '__main__':
    ensure_dirs()
    snapshot = load_snapshot()
    candidates = read_json(OUTPUTS_DIR / 'target_candidates.json', {'candidates': {}})
    matrix = build_target_matrix(snapshot)
    # Build target recommendations
    recommendations = {}
    for branch, data in matrix.get('branches', {}).items():
        if data.get('requires_user_decision') and not data.get('confirmed_targets'):
            recommendations[branch] = {'recommended_action': 'ask_user', 'because': ['target intent required']}
        elif data.get('candidate_targets') and len(data['candidate_targets']) > 1:
            recommendations[branch] = {'recommended_action': 'choose_target', 'because': ['multiple candidates']}
        elif data.get('declared_target') and data.get('confirmed_targets') and data['declared_target'] != data['confirmed_targets'][0]:
            recommendations[branch] = {'recommended_action': 'retarget_pr', 'declared': data['declared_target'], 'inferred': data['confirmed_targets'][0]}
    write_json(OUTPUTS_DIR / 'target_matrix.json', matrix)
    write_json(OUTPUTS_DIR / 'target_recommendations.json', recommendations)
    print(json.dumps({'matrix': matrix, 'recommendations': recommendations}, indent=2))
