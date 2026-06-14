#!/usr/bin/env python3
"""Calculate stacking order per target root."""
import json
from pathlib import Path
from datetime import datetime, timezone
from agent_core import OUTPUTS_DIR, ensure_dirs, write_json, read_json, current_decisions

def build_stack_order():
    """Build executable stacks per target root."""
    plan = read_json(OUTPUTS_DIR / 'execution_plan.json', {})
    snapshot = read_json(OUTPUTS_DIR / 'analysis_snapshot.json', {})
    nodes = snapshot.get('branch_graph', {}).get('nodes', {})
    decisions = current_decisions()
    root_decisions = {}
    for branch, node in nodes.items():
        for ev in decisions.values():
            if ev.get('branch') == branch and 'do_not_refresh_root' in ev.get('choice', ''):
                root_decisions[node.get('root_branch')] = ev
            if ev.get('branch') == branch and 'create_clean_integration_base' in ev.get('choice', ''):
                root_decisions[node.get('root_branch')] = ev
    # Check if any branch indicates stale/blocked root
    blocked_roots = set()
    for branch, node in nodes.items():
        root = node.get('root_branch') or 'unknown'
        if node.get('status') in {'blocked_merge_commits', 'cross_root_conflict', 'manual_triage', 'unrooted'}:
            blocked_roots.add(root)
    targets = {}
    exec_q = plan.get('execution_queue', [])
    # Initialize all roots with their blocked status
    all_roots = set()
    for branch, node in nodes.items():
        all_roots.add(node.get('root_branch') or 'unknown')
    for root in all_roots:
        is_blocked = root in blocked_roots
        targets[root] = {
            'root_health': 'stale' if is_blocked else 'current',
            'execution_allowed': not is_blocked,
            'stacks': [],
            'blocked_reason': 'in_target_conflict_resolution_merge' if is_blocked and root in blocked_roots else None
        }
    # Group executable branches by root
    by_root = {}
    for item in exec_q:
        root = item.get('root_branch', 'unknown')
        if root not in by_root:
            by_root[root] = []
        by_root[root].append(item)
    for root, branches in by_root.items():
        if root not in targets:
            targets[root] = {'root_health': 'current', 'execution_allowed': True, 'stacks': []}
        # Skip if root is blocked
        if not targets[root].get('execution_allowed', True):
            continue
        sorted_branches = sorted(branches, key=lambda x: x.get('order', 0))
        targets[root]['stacks'] = [{
            'stack_id': f'stack-{root.replace("/", "-")}-001',
            'branches': [{'branch': b['branch'], 'order': i+1, 'action': b.get('action')} for i, b in enumerate(sorted_branches)]
        }]
    return {'generated_at_utc': datetime.now(timezone.utc).isoformat(), 'targets': targets}

if __name__ == '__main__':
    ensure_dirs()
    stacks = build_stack_order()
    write_json(OUTPUTS_DIR / 'stack_order.json', stacks)
    print(json.dumps(stacks, indent=2))