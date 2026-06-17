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
        if not data.get('requires_user_decision'):
            continue
        counter += 1
        diag = data.get('diagnostic_category', '')
        if diag == 'in_target_conflict_resolution_merge':
            options = ["linearise_and_proceed", "proceed_with_target=main", "leave_triage", "exclude_from_migration"]
            question = f"This branch has merged its target to resolve conflicts. How should {branch} proceed?"
        elif diag == 'cross_root_contamination':
            options = ["target=main", "leave_triage", "exclude_from_migration"]
            question = f"This branch contains cross-root contamination. Which target should {branch} use?"
        else:
            options = ["leave_triage", "exclude_from_migration"]
            for ct in data.get('candidate_targets', []):
                options.insert(0, f"target={ct['target']}")
            if data.get('confirmed_targets'):
                options.insert(0, f"proceed_with_target={data['confirmed_targets'][0]}")
            question = f"Which target should {branch} use?"
        questions.append({
            'id': f'q-target-{counter:06d}',
            'branch': branch,
            'question_type': 'target_intent',
            'priority': 'high',
            'reason': f"Target intent required for {branch}",
            'question': question,
            'options': options,
            'diagnostic_category': diag,
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
