#!/usr/bin/env python3
"""Validate stack order for safety before execution."""
import json
from pathlib import Path
from datetime import datetime, timezone
from agent_core import OUTPUTS_DIR, read_json, read_jsonl, write_json, ensure_dirs

def validate_stack_order():
    """Check stack order for safety violations."""
    stack_order = read_json(OUTPUTS_DIR / 'stack_order.json', {})
    plan = read_json(OUTPUTS_DIR / 'execution_plan.json', {})
    snapshot = read_json(OUTPUTS_DIR / 'analysis_snapshot.json', {})
    nodes = snapshot.get('branch_graph', {}).get('nodes', {})
    failed = []
    # Check each target
    for target, data in stack_order.get('targets', {}).items():
        if not data.get('execution_allowed', True):
            # Blocked root is fine
            continue
        stacks = data.get('stacks', [])
        for stack in stacks:
            branches = stack.get('branches', [])
            seen = set()
            for b in branches:
                branch = b.get('branch')
                if branch in seen:
                    failed.append({
                        'id': 'duplicate-branch-in-stack',
                        'severity': 'critical',
                        'branch': branch,
                        'message': f'Branch {branch} appears multiple times in stack'
                    })
                seen.add(branch)
                # Check if branch is blocked
                node = nodes.get(branch, {})
                if node.get('status') in {'blocked_merge_commits', 'cross_root_conflict', 'manual_triage', 'unrooted'}:
                    failed.append({
                        'id': 'blocked-branch-in-stack',
                        'severity': 'critical',
                        'branch': branch,
                        'message': f'Blocked branch {branch} in executable stack'
                    })
    report = {
        'status': 'pass' if not failed else 'blocked',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'failed_checks': failed,
        'next_actions': ['Run explain.py --branch <branch>' for f in failed if 'blocked' in f.get('id', '')]
    }
    write_json(OUTPUTS_DIR / 'stack_order_validation.json', report)
    return report

if __name__ == '__main__':
    ensure_dirs()
    report = validate_stack_order()
    print(json.dumps(report, indent=2))