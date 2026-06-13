#!/usr/bin/env python3
"""Validate target consistency before execution."""
import json
from pathlib import Path
from datetime import datetime, timezone
from agent_core import OUTPUTS_DIR, read_json, read_jsonl, write_json, ensure_dirs

def validate_targets():
    ensure_dirs()
    matrix = read_json(OUTPUTS_DIR / 'target_matrix.json', {})
    questions = read_json(OUTPUTS_DIR / 'target_questions.json', [])
    plan = read_json(OUTPUTS_DIR / 'execution_plan.json', {})
    failed = []
    for branch, data in matrix.get('branches', {}).items():
        if data.get('requires_user_decision') and not data.get('confirmed_targets'):
            has_q = any(q.get('branch') == branch for q in questions)
            if not has_q:
                failed.append({'id': 'missing_target_question', 'severity': 'critical', 'branch': branch, 'message': 'Target intent required but no question generated'})
        # Check if branch in execution has wrong target
        for item in plan.get('execution_queue', []):
            if item.get('branch') == branch and data.get('declared_target') and data.get('confirmed_targets'):
                if data['declared_target'] != data['confirmed_targets'][0]:
                    failed.append({'id': 'wrong_target_in_execution', 'severity': 'critical', 'branch': branch, 'message': f'Declared target {data["declared_target"]} differs from confirmed target {data["confirmed_targets"][0]}'})
    report = {
        'status': 'pass' if not failed else 'blocked',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'failed_checks': failed,
        'next_actions': [f'Run target_questions.py --branch {f["branch"]}' for f in failed if 'question' in f['id']]
    }
    write_json(OUTPUTS_DIR / 'target_validation_report.json', report)
    return report

if __name__ == '__main__':
    report = validate_targets()
    print(json.dumps(report, indent=2))
