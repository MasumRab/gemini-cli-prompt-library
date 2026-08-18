from .constants import BLOCKED_EDGE_TYPES, EXECUTABLE_EDGE_TYPES, EXECUTABLE_STATUSES


class ConservativeGraphitePolicy:
    def can_execute_branch(self, node):
        inv = node.audit.invariants
        return (
            node.status in EXECUTABLE_STATUSES
            and bool(node.resolved_parent)
            and inv.get("single_root_owner") is True
            and inv.get("cycle_free") is True
            and inv.get("no_blocked_relationships") is True
            and inv.get("has_executable_parent") is True
            and inv.get("root_branch_resolved") is True
        )

    def is_executable_edge(self, edge):
        return (
            edge.classification == "executable"
            and edge.edge_type in EXECUTABLE_EDGE_TYPES
        )

    def is_blocked_edge(self, edge):
        return edge.classification == "blocked" or edge.edge_type in BLOCKED_EDGE_TYPES
