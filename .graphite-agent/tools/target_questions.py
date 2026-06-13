#!/usr/bin/env python3
"""Show target-intent questions."""
import argparse
import json
from pathlib import Path
from agent_core import OUTPUTS_DIR, read_json, write_json, ensure_dirs

def build_target_questions(matrix):
    """Build target questions for branches requiring decisions."""
    questions = []
    counter = 0
    for branch, data in matrix.get('branches', {}).items():
        if data.get('requires_user_decision') and not data.get('confirmed_targets'):
            counter += 1
            options = ["leave_triage", "exclude_from_migration"]
            for ct in data.get('candidate_targets', []):
                options.insert(0, f"target={ct['target']}")
            questions.append({
                'id': f'q-target-{counter:06d}',
                'branch': branch,
                'question_type': 'target_intent',
                'priority': 'high',
                'reason': f"Target intent required for {branch}",
                'question': f"Which target should {branch} use?",
                'options': options,
                'diagnostic_category': data.get('diagnostic_category', 'target_intent_required'),
                'confidence': 'medium'
            })
    return questions

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--branch')
    a = p.parse_args()
    matrix = read_json(OUTPUTS_DIR / 'target_matrix.json', {'branches': {}})
    if a.branch:
        matrix = {'branches': {a.branch: matrix.get('branches', {}).get(a.branch, {})}}
    questions = build_target_questions(matrix)
    write_json(OUTPUTS_DIR / 'target_questions.json', questions)
    for q in questions:
        print(json.dumps(q, indent=2))

if __name__ == '__main__':
    main()
