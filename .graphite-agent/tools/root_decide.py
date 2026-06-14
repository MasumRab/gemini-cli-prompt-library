#!/usr/bin/env python3
"""Record root-refresh decisions."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from agent_core import OUTPUTS_DIR, ensure_dirs, read_json, next_id, append_jsonl

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--branch', required=True)
    p.add_argument('--choice', required=True)
    p.add_argument('--reason', required=True)
    a = p.parse_args()
    snapshot = read_json(OUTPUTS_DIR / 'analysis_snapshot.json', {})
    nodes = snapshot.get('branch_graph', {}).get('nodes', {})
    branch = a.branch
    if branch not in nodes:
        raise RuntimeError(f"Branch not found: {branch}")
    node = nodes[branch]
    root = node.get('root_branch', node.get('inferred_target', 'main'))
    event = {
        'event_id': next_id('dec-root', OUTPUTS_DIR / 'decision_log.jsonl'),
        'event_type': 'decision_recorded',
        'decision_type': 'root_refresh_policy',
        'target_root': root,
        'branch': branch,
        'choice': a.choice,
        'reason': a.reason,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    append_jsonl(OUTPUTS_DIR / 'decision_log.jsonl', event)
    print(json.dumps(event, indent=2))

if __name__ == '__main__':
    main()