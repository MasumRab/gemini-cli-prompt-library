#!/usr/bin/env python3
"""Validate root health before execution."""
import json
from pathlib import Path
from datetime import datetime, timezone
from agent_core import OUTPUTS_DIR, read_json, read_jsonl, write_json, ensure_dirs

def validate_roots():
    """Check that stale roots don't have executable branches without decisions."""
    root_health = read_json(OUTPUTS_DIR / 'root_health.json', {})
    stack_order = read_json(OUTPUTS_DIR / 'stack_order.json', {})
    decisions = read_jsonl(OUTPUTS_DIR / 'decision_log.jsonl')
    failed = []
    # Check each root
    for root, health in root_health.get('roots', {}).items():
        if health.get('health') == 'stale':
            # Check if any branches from this root are executable
            so_data = stack_order.get('targets', {}).get(root, {})
            has_decision = any('do_not_refresh_root' in str(d.get('choice', '')) for d in decisions)
            if so_data.get('execution_allowed', True) and not has_decision:
                failed.append({
                    'id': 'stale-root-affects-execution',
                    'severity': 'critical',
                    'target_root': root,
                    'message': f'{root} is stale and has executable branches without root-refresh decision'
                })
            elif not so_data.get('execution_allowed', True):
                # Root is correctly blocked
                pass
    report = {
        'status': 'pass' if not failed else 'blocked',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'failed_checks': failed,
        'next_actions': [f'Run root_questions.py --target {f["target_root"]}' for f in failed if 'root' in f.get('id', '')]
    }
    write_json(OUTPUTS_DIR / 'root_validation_report.json', report)
    return report

if __name__ == '__main__':
    ensure_dirs()
    report = validate_roots()
    print(json.dumps(report, indent=2))