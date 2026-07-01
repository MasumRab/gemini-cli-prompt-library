from .io import now

def generate_stack_order(nodes, root_health_data, EXECUTABLE):
    out = {'generated_at_utc': now(), 'targets': {}}
    for t, h in root_health_data.items():
        allowed = h.get('execution_allowed')
        branches = []
        if allowed:
            for b, n in nodes.items():
                if n.get('root_branch') == t and n.get('status') in EXECUTABLE:
                    branches.append({
                        'branch': b,
                        'order': len(branches) + 1,
                        'action': 'track_and_restack' if n.get('status') == 'needs_restack' else 'track_only',
                        'resolved_parent': n.get('resolved_parent')
                    })
        out['targets'][t] = {
            'root_health': h.get('health'),
            'execution_allowed': allowed,
            'blocked_reason': None if allowed else h.get('recommended_action'),
            'stacks': [{'stack_id': f'stack-{t}-0001', 'branches': branches}] if branches else []
        }
    return out
