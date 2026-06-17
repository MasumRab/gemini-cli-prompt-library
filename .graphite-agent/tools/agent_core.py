#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure the local lib directory is on the path
lib_path = Path(__file__).parent.resolve()
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

from lib.io import rj, wj, now
from lib.decisions import append_decision, decisions, current_decisions, nextid
from lib.relationships import relationship_graph as lib_relationship_graph
from lib.targets import discover_targets as lib_discover_targets, target_analyse as lib_target_analyse
from lib.roots import root_health as lib_root_health
from lib.stack_ordering import generate_stack_order

AGENT_DIR = Path('.graphite-agent')
OUTPUTS_DIR = AGENT_DIR / 'outputs'
DECISION_LOG = OUTPUTS_DIR / 'decision_log.jsonl'

EXECUTABLE = {'safe', 'needs_restack'}
BLOCKED = {'blocked_merge_commits', 'manual_triage', 'cross_root_conflict', 'unrooted'}

def nodes(s):
    return s.get('branch_graph', {}).get('nodes', {}) or s.get('branch_state', {}) or {}

def snap():
    s = rj(OUTPUTS_DIR / 'analysis_snapshot.json') or rj(AGENT_DIR / 'analysis_snapshot.json')
    if not s:
        raise RuntimeError('analysis_snapshot.json missing')
    return s

def plan():
    p = rj(OUTPUTS_DIR / 'execution_plan.json') or rj(AGENT_DIR / 'plan.json')
    if not p:
        raise RuntimeError('plan.json missing')
    return p

def relationship_graph(s):
    if s.get('relationship_graph', {}).get('edges'):
        return s['relationship_graph']
    return lib_relationship_graph(nodes(s), EXECUTABLE, BLOCKED)

def triage_packets(s, rel):
    out = {}
    i = 0
    for b, n in nodes(s).items():
        if n.get('status') in EXECUTABLE:
            continue
        i += 1
        reason = n.get('reason') or ''
        cat = n.get('diagnostic_category') or ('in_target_conflict_resolution_merge' if n.get('status') == 'blocked_merge_commits' and 'merge' in reason.lower() else n.get('status'))
        out[b] = {
            'id': f'triage-{i:06d}',
            'branch': b,
            'status': n.get('status'),
            'diagnostic_category': cat,
            'root_branch': n.get('root_branch'),
            'primary_reason': reason,
            'relationship_edges': [e['id'] for e in rel['edges'] if e.get('from') == b or e.get('to') == b],
            'recommended_action': 'linearise_before_graphite_tracking' if cat == 'in_target_conflict_resolution_merge' else 'manual_review_required',
            'next_steps': [f'explain.py --branch {b}', f'questions.py --branch {b}', 'validate_plan.py']
        }
    return out

def questions(triage):
    q = []
    i = 0
    for b, t in triage.items():
        if t['status'] not in {'manual_triage', 'unrooted'}:
            continue
        i += 1
        opts = ['leave_triage', 'exclude_from_migration']
        if t.get('root_branch'):
            opts.insert(0, 'parent=' + t['root_branch'])
        q.append({
            'id': f'q-{i:06d}',
            'branch': b,
            'priority': 'high',
            'question': f'Choose intended handling for {b}.',
            'options': opts,
            'recommended_option': 'leave_triage',
            'confidence': 'medium'
        })
    return q

def summary(s, p):
    bs = {}
    br = {}
    idx = {k: [] for k in ['safe_branches', 'needs_restack_branches', 'cross_root_branches', 'merge_blocked_branches', 'unrooted_branches', 'manual_triage_branches']}
    mp = {'safe': 'safe_branches', 'needs_restack': 'needs_restack_branches', 'cross_root_conflict': 'cross_root_branches', 'blocked_merge_commits': 'merge_blocked_branches', 'unrooted': 'unrooted_branches', 'manual_triage': 'manual_triage_branches'}
    for b, n in nodes(s).items():
        st = n.get('status', 'unknown')
        rt = n.get('root_branch') or '<none>'
        bs[st] = bs.get(st, 0) + 1
        br[rt] = br.get(rt, 0) + 1
        if st in mp:
            idx[mp[st]].append(b)
    return {
        'metadata': s.get('metadata', {}),
        'counts': {
            'branches_total': len(nodes(s)),
            'execution_queue': len(p.get('execution_queue', [])),
            'manual_triage_queue': len(p.get('manual_triage_queue', []))
        },
        'by_status': bs,
        'by_root': br,
        'indexes': idx
    }

def analyse_outputs():
    s = snap(); p = plan(); rel = relationship_graph(s); tri = triage_packets(s, rel); qs = questions(tri)
    rec = {b: {'branch': b, 'recommended_action': ('track_and_restack' if n.get('status') == 'needs_restack' else 'track_only') if n.get('status') in EXECUTABLE else 'block_or_ask_user', 'because': [n.get('reason')]} for b, n in nodes(s).items()}
    for name, obj in [('analysis_summary.json', summary(s, p)), ('relationship_graph.json', rel), ('triage_packets.json', tri), ('question_queue.json', qs), ('recommendations.json', rec)]:
        wj(OUTPUTS_DIR / name, obj)
    if not DECISION_LOG.exists():
        DECISION_LOG.write_text('')
    current_decisions()
    return summary(s, p)

def discover_targets():
    s = snap(); configured_roots = s.get('metadata', {}).get('configured_roots', [])
    out = lib_discover_targets(nodes(s), configured_roots)
    wj(OUTPUTS_DIR / 'target_candidates.json', out)
    return out

def target_analyse():
    s = snap(); targets = discover_targets(); branches, qs, rec = lib_target_analyse(nodes(s), targets['candidates'])
    wj(OUTPUTS_DIR / 'target_matrix.json', {'generated_at_utc': now(), 'branches': branches})
    wj(OUTPUTS_DIR / 'target_questions.json', qs)
    wj(OUTPUTS_DIR / 'target_recommendations.json', rec)
    return branches

def root_health():
    s = snap(); targets = discover_targets()['candidates']; roots, qs, rec = lib_root_health(nodes(s), targets, BLOCKED)
    wj(OUTPUTS_DIR / 'root_health.json', {'generated_at_utc': now(), 'roots': roots})
    wj(OUTPUTS_DIR / 'root_refresh_questions.json', qs)
    wj(OUTPUTS_DIR / 'root_refresh_recommendations.json', rec)
    return roots

def stack_order():
    s = snap(); rh = rj(OUTPUTS_DIR / 'root_health.json') or {'roots': root_health()}
    out = generate_stack_order(nodes(s), rh['roots'], EXECUTABLE)
    wj(OUTPUTS_DIR / 'stack_order.json', out)
    return out

def validate_plan():
    analyse_outputs(); tri = rj(OUTPUTS_DIR / 'triage_packets.json', {}); p = plan(); fail = []
    for e in p.get('execution_queue', []):
        if e.get('status') not in EXECUTABLE: fail.append({'id': 'unsafe-status', 'branch': e.get('branch')})
        if not e.get('resolved_parent'): fail.append({'id': 'missing-parent', 'branch': e.get('branch')})
        if e.get('branch') in tri: fail.append({'id': 'branch-in-triage-and-execution', 'branch': e.get('branch')})
    rep = {'status': 'blocked' if fail else 'pass', 'failed_checks': fail}
    wj(OUTPUTS_DIR / 'checklist_report.json', rep)
    return rep

def run_diagnostics(write=False):
    return analyse_outputs()

def validation_report():
    return {'status': 'pass'}
