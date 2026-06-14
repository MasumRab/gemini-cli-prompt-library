#!/usr/bin/env python3
"""Analyse root health relative to main/other baselines."""
import json
from pathlib import Path
from datetime import datetime, timezone
from agent_core import OUTPUTS_DIR, ensure_dirs, write_json, read_json, read_jsonl, next_id

def assess_root_health(snapshot):
    nodes = snapshot.get('branch_graph', {}).get('nodes', {})
    metadata = snapshot.get('metadata', {})
    default_root = metadata.get('default_root', 'main')
    roots = {}
    for branch, node in nodes.items():
        root = node.get('root_branch')
        if root and root not in roots:
            roots[root] = {'branch': root, 'health': 'current', 'relative_to': default_root, 'diagnostic_category': 'root_current', 'evidence': [], 'affected_branches': [], 'recommended_action': 'stack_order_allowed', 'execution_allowed': True}
    for branch, node in nodes.items():
        root = node.get('root_branch')
        audit = node.get('audit', {})
        merge = audit.get('merge_analysis', {})
        if merge.get('trunk_updates'):
            if root in roots:
                roots[root]['health'] = 'stale'
                roots[root]['diagnostic_category'] = 'shared_root_staleness'
                roots[root]['execution_allowed'] = False
                roots[root]['evidence'].append(f'{branch} has trunk update merge for conflict resolution')
                roots[root]['affected_branches'].append(branch)
                roots[root]['recommended_action'] = 'root_refresh_decision_required'
    return {'generated_at_utc': datetime.now(timezone.utc).isoformat(), 'roots': roots}

def build_root_questions(roots):
    questions = []
    for root, data in roots.items():
        if data.get('health') != 'stale':
            continue
        relative_to = data.get('relative_to', 'main')
        questions.append({
            'id': next_id('q-root', OUTPUTS_DIR / 'decision_log.jsonl'),
            'target_root': root,
            'question_type': 'root_refresh_policy',
            'priority': 'high',
            'question': f"Many branches from {root} appear stale relative to {relative_to}. How should this target root be handled before stacking dependent branches?",
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

def main():
    ensure_dirs()
    snapshot = read_json(OUTPUTS_DIR / 'analysis_snapshot.json')
    health = assess_root_health(snapshot)
    write_json(OUTPUTS_DIR / 'root_health.json', health)
    questions = build_root_questions(health.get('roots', {}))
    write_json(OUTPUTS_DIR / 'root_refresh_questions.json', questions)
    recs = {}
    for root, data in health.get('roots', {}).items():
        if data.get('health') == 'stale':
            recs[root] = {
                'recommended_action': 'root_refresh_decision_required',
                'confidence': 'medium',
                'why': data.get('evidence', []),
                'affected_branch_count': len(data.get('affected_branches', [])),
                'affected_branches': data.get('affected_branches', []),
                'next_command': f'python .graphite-agent/tools/root_decide.py --target {root}'
            }
    write_json(OUTPUTS_DIR / 'root_refresh_recommendations.json', recs)
    print(json.dumps({'root_health': health, 'questions': questions}, indent=2))

if __name__ == '__main__':
    main()
