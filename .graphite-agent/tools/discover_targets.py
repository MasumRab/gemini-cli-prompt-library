#!/usr/bin/env python3
"""Discover candidate target branches from remote refs and PR patterns."""
import json
import subprocess
from pathlib import Path
from collections import defaultdict
from agent_core import OUTPUTS_DIR, ensure_dirs, write_json

def get_remote_branches():
    """Get all remote branches, filtering out invalid refs."""
    out = subprocess.run(['git', 'branch', '-r'], capture_output=True, text=True)
    branches = []
    for line in out.stdout.strip().splitlines():
        line = line.strip()
        if line and line != 'HEAD' and line.startswith('origin/'):
            branch = line.replace('origin/', '')
            if '/' in branch or branch in ('main', 'master'):  # Only include valid branches
                branches.append(branch)
    return branches

def get_pr_bases():
    """Get PR base references from gh API."""
    try:
        r = subprocess.run(['gh', 'repo', 'view', '--json', 'owner,name'], capture_output=True, text=True)
        d = json.loads(r.stdout)
        owner = d['owner']['login']
        repo = d['name']
        out = subprocess.run(['gh', 'api', f'repos/{owner}/{repo}/pulls?state=open&per_page=100'], capture_output=True, text=True)
        prs = json.loads(out.stdout or '[]')
        return [p['base']['ref'] for p in prs if p.get('base')]
    except:
        return []

def score_targets(branches, pr_bases):
    """Score branches as potential targets."""
    scores = defaultdict(lambda: {'signals': [], 'count': 0})
    pr_base_count = defaultdict(int)
    for base in pr_bases:
        pr_base_count[base] += 1
    for b in branches:
        if pr_base_count[b] > 0:
            scores[b]['signals'].append('used_as_pr_base')
            scores[b]['count'] += 10
        if b in ('main', 'master'):
            scores[b]['signals'].append('standard_trunk')
            scores[b]['count'] += 50
        scores[b]['confidence'] = 'high' if scores[b]['count'] >= 50 else 'medium' if scores[b]['count'] >= 20 else 'low'
    return {k: dict(v) for k, v in scores.items() if v['count'] > 0 or k in ('main', 'master')}

def discover_targets():
    branches = get_remote_branches()
    pr_bases = get_pr_bases()
    scored = score_targets(branches, pr_bases)
    return {'generated_at_utc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(), 'candidates': scored}

if __name__ == '__main__':
    ensure_dirs()
    targets = discover_targets()
    write_json(OUTPUTS_DIR / 'target_candidates.json', targets)
    print(json.dumps(targets, indent=2))
