#!/usr/bin/env python3
"""Generate root-refresh questions."""
import json
from pathlib import Path
from agent_core import OUTPUTS_DIR, ensure_dirs, write_json, read_json, next_id

def build_root_questions(root_health):
    questions = []
    for root, data in root_health.get('roots', {}).items():
        if data.get('health') != 'stale':
            continue
        questions.append({
            'id': next_id('q-root', OUTPUTS_DIR / 'decision_log.jsonl'),
            'target_root': root,
            'question_type': 'root_refresh_policy',
            'priority': 'high',
            'question': f"Many branches from {root} appear stale relative to main. How should this target root be handled before stacking dependent branches?",
            'options': [
                f"target={root}",
                'do_not_refresh_root',
                'create_clean_integration_base',
                'leave_affected_branches_triage'
            ],
            'recommended_option': 'create_clean_integration_base',
            'confidence': 'medium',
            'affected_branches': data.get('affected_branches', [])
        })
    return questions

if __name__ == '__main__':
    ensure_dirs()
    health = read_json(OUTPUTS_DIR / 'root_health.json', {'roots': {}})
    questions = build_root_questions(health)
    write_json(OUTPUTS_DIR / 'root_refresh_questions.json', questions)
    print(json.dumps(questions, indent=2))