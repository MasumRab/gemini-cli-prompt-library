#!/usr/bin/env python3
"""Preview target change consequences."""
import argparse
import json
from pathlib import Path
from agent_core import read_json

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--branch')
    p.add_argument('--target')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    snapshot = read_json(Path('.graphite-agent/outputs/analysis_snapshot.json'))
    nodes = snapshot.get('branch_graph', {}).get('nodes', {})
    node = nodes.get(a.branch, {})
    change = {'resolved_parent': {'from': node.get('resolved_parent'), 'to': a.target}}
    print(json.dumps({'mode': 'dry_run' if a.dry_run else 'live', 'branch': a.branch, 'proposed_choice': f'target={a.target}', 'would_change': change, 'relationships': node.get('relationship_edges', [])}, indent=2))

if __name__ == '__main__':
    main()
