from .io import wj, now

def discover_targets(nodes, configured_roots):
    cand = {}
    for r in configured_roots:
        cand[r] = {'target': r, 'score': 80, 'confidence': 'high', 'signals': ['configured root']}
    for n in nodes.values():
        r = n.get('root_branch')
        if r and r not in cand:
            cand[r] = {'target': r, 'score': 70, 'confidence': 'medium', 'signals': ['root_branch in analysis']}
    return {'generated_at_utc': now(), 'candidates': cand}

def target_analyse(nodes, candidate_targets):
    branches = {}
    qs = []
    rec = {}
    i = 0
    for b, n in nodes.items():
        declared = n.get('declared_base')
        inferred = n.get('root_branch')
        cat = 'target_confirmed' if declared == inferred or not declared else 'wrong_pr_target_candidate' if inferred and declared != inferred else 'target_intent_required'
        req = cat != 'target_confirmed'
        qrefs = []
        if req:
            i += 1
            qid = f'q-target-{i:06d}'
            qrefs = [qid]
            opts = []
            if declared: opts.append('target=' + declared)
            if inferred: opts.append('target=' + inferred)
            if declared and inferred and declared != inferred: opts.append(f'targets={declared}+{inferred}')
            opts += ['leave_triage', 'exclude_from_migration']
            qs.append({
                'id': qid,
                'branch': b,
                'question_type': 'target_intent',
                'priority': 'high',
                'question': f'Which target should {b} use?',
                'options': opts,
                'recommended_option': 'target=' + inferred if inferred else 'leave_triage',
                'confidence': 'medium'
            })
        branches[b] = {
            'declared_target': declared,
            'candidate_targets': [{'target': x, 'confidence': 'medium', 'evidence': ['declared/inferred target']} for x in [declared, inferred] if x],
            'confirmed_targets': [],
            'diagnostic_category': cat,
            'requires_user_decision': req,
            'question_refs': qrefs
        }
        rec[b] = {'recommended_action': 'resolve_target_intent' if req else 'keep_declared_target', 'confidence': 'medium', 'because': [cat]}
    return branches, qs, rec
