#!/usr/bin/env python3
"""Validate target consistency before execution."""
import json
from pathlib import Path
from agent_core import OUTPUTS_DIR, read_json, read_jsonl

def validate_targets():
    """Check for unresolved target ambiguity."""
    matrix = read_json(OUTPUTS_DIR / 'target_matrix.json', {})
    questions = read_json(OUTPUTS_DIR / 'target_questions.json', [])
    failed = []
    for branch, data in matrix.get('branches', {}).items():
        if data.get('requires_user_decision'):
            has_q = any(q.get('branch') == branch for q in questions)
            if not has_q:
                failed.append({'id': 'missing_target_question', 'severity': 'critical', 'branch': branch, 'message': 'Target intent required but no question generated'})
    return {'status': 'pass' if not failed else 'blocked', 'failed_checks': failed}

if __name__ == '__main__':
    report = validate_targets()
    print(json.dumps(report, indent=2))
