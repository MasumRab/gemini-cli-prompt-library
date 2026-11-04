from .models import BranchNode


class BranchClassifier:
    def __init__(self, config, verifier, policy):
        self.config = config
        self.verifier = verifier
        self.policy = policy

    def classify(self, pr, relationship_edges, has_cycle=False):
        branch = pr.head_ref_name
        branch_edges = [
            e for e in relationship_edges if e.from_ref == branch or e.to_ref == branch
        ]
        inbound = [e for e in relationship_edges if e.to_ref == branch]
        executable = [e for e in inbound if self.policy.is_executable_edge(e)]
        blocked = [e for e in branch_edges if self.policy.is_blocked_edge(e)]
        patch_only = not executable and any(
            e.edge_type == "patch_id_overlap" for e in branch_edges
        )
        parent = executable[0].from_ref if executable else None
        root = executable[0].root_branch if executable else None
        ambiguous = not parent and not patch_only and not blocked
        audit = self.verifier.verify(
            branch,
            root,
            parent,
            bool(executable),
            bool(blocked),
            has_cycle,
            ambiguous,
            patch_only,
        )
        status, reason = self._status_from_inputs(
            audit, executable, blocked, patch_only, ambiguous
        )
        return BranchNode(
            branch,
            root,
            parent if status in {"safe", "needs_restack"} else None,
            status,
            reason,
            audit,
            [e.id for e in branch_edges],
            self._risk_annotations(pr),
        )

    def _status_from_inputs(self, audit, executable, blocked, patch_only, ambiguous):
        if not audit.invariants["root_branch_resolved"]:
            return "unrooted", "No configured root owner found."
        if not audit.invariants["single_root_owner"]:
            return "cross_root_conflict", "Branch has multiple configured root owners."
        if not audit.invariants["cycle_free"]:
            return "cycle", "Cycle detected in executable candidate graph."
        if blocked:
            return (
                "blocked_merge_commits",
                "Branch has blocked merge or cross-root evidence.",
            )
        if executable:
            return (
                (
                    "needs_restack",
                    "Executable same-root parent exists but ancestry is stale.",
                )
                if executable[0].status == "needs_restack"
                else ("safe", "Declared parent is same-root ancestor.")
            )
        if patch_only:
            return (
                "patch_equivalence_only",
                "Patch overlap exists but no executable ancestry relationship exists.",
            )
        return (
            "ambiguous_relationship",
            "No safe Graphite parent relationship could be derived.",
        )

    def _risk_annotations(self, pr):
        anns = []
        if pr.is_draft:
            anns.append(
                {
                    "type": "draft_pr",
                    "classification": "informational",
                    "evidence": ["isDraft=true"],
                }
            )
        if pr.merge_state_status:
            anns.append(
                {
                    "type": "mergeability_state",
                    "classification": "informational",
                    "evidence": [f"mergeStateStatus={pr.merge_state_status}"],
                }
            )
        if pr.review_decision:
            anns.append(
                {
                    "type": "review_state",
                    "classification": "informational",
                    "evidence": [f"reviewDecision={pr.review_decision}"],
                }
            )
        return anns
