from .constants import (
    EXECUTABLE_STATUSES,
    GRAPHITE_ACTIONS,
    RELATIONSHIP_CLASSIFICATIONS,
)


def validate_execution_plan(plan):
    if "execution_queue" not in plan:
        raise ValueError("execution_plan missing execution_queue")
    for step in plan["execution_queue"]:
        for key in [
            "id",
            "branch",
            "resolved_parent",
            "root_branch",
            "status",
            "action",
            "relationship_edges",
            "preconditions",
        ]:
            if key not in step:
                raise ValueError(f"execution step missing {key}: {step}")
        if step["status"] not in EXECUTABLE_STATUSES:
            raise ValueError(f"non-executable status: {step}")
        if step["action"] not in GRAPHITE_ACTIONS:
            raise ValueError(f"unsupported action: {step}")


def validate_relationship_graph(graph):
    if "edges" not in graph:
        raise ValueError("relationship_graph missing edges")
    for edge in graph["edges"]:
        for key in [
            "id",
            "from_ref",
            "to_ref",
            "edge_type",
            "classification",
            "status",
            "confidence",
            "root_branch",
            "evidence",
        ]:
            if key not in edge:
                raise ValueError(f"edge missing {key}: {edge}")
        if edge["classification"] not in RELATIONSHIP_CLASSIFICATIONS:
            raise ValueError(f"unsupported classification: {edge}")
