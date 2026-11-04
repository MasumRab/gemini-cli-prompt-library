from .io import now


def root_health(nodes, candidate_targets, BLOCKED, active_decisions=None):
    if active_decisions is None:
        active_decisions = {}
    roots = {}
    qs = []
    rec = {}
    i = 0
    for t in candidate_targets:
        affected = [b for b, n in nodes.items() if n.get("root_branch") == t]
        stale = sum(1 for b in affected if nodes[b].get("status") in BLOCKED) >= 2

        # Check if a decision overrides the stale state
        decision_exists = any(
            d.get("branch") == t or d.get("target_root") == t
            for d in active_decisions.values()
        )

        execution_allowed = not stale or decision_exists

        roots[t] = {
            "health": "stale" if stale else "current",
            "relative_to": "unknown",
            "diagnostic_category": "shared_root_staleness" if stale else "root_current",
            "evidence": (
                ["multiple blocked/manual branches from this root"]
                if stale
                else ["no shared blocker detected"]
            ),
            "affected_branches": affected,
            "recommended_action": (
                "stack_order_allowed"
                if execution_allowed
                else "root_refresh_decision_required"
            ),
            "execution_allowed": execution_allowed,
        }
        if stale and not decision_exists:
            i += 1
            qs.append(
                {
                    "id": f"q-root-{i:06d}",
                    "target_root": t,
                    "question_type": "root_refresh_policy",
                    "priority": "high",
                    "question": f"Many branches from {t} appear stale. How should this target root be handled?",
                    "options": [
                        "refresh_root_before_stacking",
                        "create_clean_integration_base",
                        "do_not_refresh_root",
                        "leave_affected_branches_triage",
                    ],
                    "recommended_option": "create_clean_integration_base",
                    "confidence": "medium",
                    "affected_branches": affected,
                }
            )
            rec[t] = {
                "recommended_action": "root_refresh_decision_required",
                "affected_branches": affected,
                "next_command": f"root_questions.py --target {t}",
            }
    return roots, qs, rec
