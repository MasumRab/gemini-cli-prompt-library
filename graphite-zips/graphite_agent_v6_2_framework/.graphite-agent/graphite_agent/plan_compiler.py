from .constants import EXECUTABLE_STATUSES


class PlanCompiler:
    def __init__(self, ids, policy, schema_version):
        self.ids = ids
        self.policy = policy
        self.schema_version = schema_version

    def compile_execution_plan(self, branch_nodes):
        queue = []
        for branch, node in branch_nodes.items():
            if self.policy.can_execute_branch(node):
                queue.append(
                    {
                        "id": self.ids.execution_id(),
                        "branch": branch,
                        "resolved_parent": node.resolved_parent,
                        "root_branch": node.root_branch,
                        "status": node.status,
                        "action": (
                            "track_and_restack"
                            if node.status == "needs_restack"
                            else "track_only"
                        ),
                        "relationship_edges": node.relationship_edges,
                        "preconditions": node.audit.invariants,
                    }
                )
        return {"schema_version": self.schema_version, "execution_queue": queue}

    def compile_triage_packets(self, branch_nodes):
        packets = {}
        for branch, node in branch_nodes.items():
            if node.status in EXECUTABLE_STATUSES:
                continue
            pid = self.ids.triage_id()
            packets[pid] = {
                "id": pid,
                "branch": branch,
                "status": node.status,
                "root_branch": node.root_branch,
                "primary_reason": node.reason,
                "relationship_edges": node.relationship_edges,
                "candidate_parents": [],
                "risk_annotations": node.risk_annotations,
                "recommended_action": "manual review; do not auto-track",
                "detail_refs": {
                    "branch_node_ref": f"analysis_snapshot.branch_graph.nodes.{branch}",
                    "relationship_edges": node.relationship_edges,
                },
            }
        return {"schema_version": self.schema_version, "packets": packets}
