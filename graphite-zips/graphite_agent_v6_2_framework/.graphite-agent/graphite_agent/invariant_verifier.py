from .models import BranchAudit


class InvariantVerifier:
    def __init__(self, config, git):
        self.config = config
        self.git = git

    def root_owner_candidates(self, branch):
        candidates = []
        for root in self.config.configured_roots:
            mb = self.git.merge_base(root, branch)
            if not mb:
                continue
            candidates.append(
                {
                    "root": root,
                    "merge_base": mb,
                    "dist": self.git.commit_distance(mb, branch),
                    "is_ancestor": self.git.is_ancestor(root, branch),
                }
            )
        return sorted(
            candidates, key=lambda x: x["dist"] if x["dist"] is not None else 10**9
        )

    def verify(
        self,
        branch,
        root_branch,
        resolved_parent,
        executable_parent_exists,
        has_blocked_edges,
        has_cycle,
        ambiguous,
        patch_overlap_only,
    ):
        candidates = self.root_owner_candidates(branch)
        owners = [c for c in candidates if c["is_ancestor"]]
        invariants = {
            "single_root_owner": len(owners) == 1,
            "cycle_free": not has_cycle,
            "no_cycles": not has_cycle,
            "parent_exists": bool(resolved_parent),
            "no_ambiguous_lineage": not ambiguous,
            "no_patch_overlap": not patch_overlap_only,
            "no_blocked_relationships": not has_blocked_edges,
            "has_executable_parent": executable_parent_exists,
            "root_branch_resolved": bool(root_branch),
            "topological_valid": not has_cycle,
        }
        failed = [k for k, v in invariants.items() if not v]
        return BranchAudit(
            root_owner={
                "selected": root_branch,
                "candidates": candidates,
                "ambiguous": len(owners) != 1,
            },
            invariants=invariants,
            failed_invariants=failed,
            triage_reason=failed,
        )
