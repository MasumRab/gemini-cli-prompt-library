#!/usr/bin/env python3
"""Show target-intent questions."""
import argparse
import json
from pathlib import Path
from agent_core import OUTPUTS_DIR, read_json, read_jsonl

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--branch')
    a = p.parse_args()
    matrix = read_json(OUTPUTS_DIR / 'target_matrix.json', {})
    questions = []
    for branch, data in matrix.get('branches', {}).items():
        if a.branch and branch != a.branch:
            continue
        if data.get('requires_user_decision') and not data.get('confirmed_targets'):
            data['candidate_targets'] = data.get('candidate_targets') or []
            options = ['leave_triage', 'exclude_from_migration']
            for ct in data['candidate_targets']:
                options.insert(0, f"target={ct['target']}")
            if data.get('candidate_targets'):
                options.insert(0, f"targets={'+'.join(ct['target'] for ct in data['candidate_targets'])}")
            questions.append({
                'id': f'q-target-{len(questions)+1:06d}',
                'branch': branch,
                'question_type': 'target_intent',
                'priority': 'high',
                'options': options,
                'reason': f"Declared target inconsistent with inferred target for {branch}"
            })
    for q in questions:
        print(json.dumps(q))

if __name__ == '__main__':
    main()
