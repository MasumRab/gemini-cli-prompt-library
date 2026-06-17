import json
from pathlib import Path
from .io import rj, wj

AGENT_DIR = Path('.graphite-agent')
OUTPUTS_DIR = AGENT_DIR / 'outputs'
DECISION_LOG = OUTPUTS_DIR / 'decision_log.jsonl'

def append_decision(ev):
    DECISION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DECISION_LOG, 'a') as f:
        f.write(json.dumps(ev, sort_keys=True) + '\n')

def decisions():
    if not DECISION_LOG.exists():
        return []
    return [json.loads(x) for x in DECISION_LOG.read_text().splitlines() if x.strip()]

def current_decisions():
    active = {}
    superseded = set()
    revoked = set()
    for e in decisions():
        if e.get('supersedes'):
            superseded.add(e['supersedes'])
        if e.get('event_type') in {'decision_recorded', 'decision_revised'}:
            active[e.get('branch') or e.get('target_root')] = e
        if e.get('event_type') == 'decision_revoked':
            revoked.add(e.get('target_decision_id'))
    cur = {k: v for k, v in active.items() if v.get('event_id') not in superseded and v.get('event_id') not in revoked}
    wj(OUTPUTS_DIR / 'current_decisions.json', cur)
    return cur

def nextid(prefix):
    return f'{prefix}-{len(decisions()) + 1:06d}'
