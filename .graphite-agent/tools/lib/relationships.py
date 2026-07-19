

def relationship_graph(nodes, EXECUTABLE, BLOCKED):
    edges = []
    i = 0
    for b, n in nodes.items():
        st = n.get("status")
        parent = n.get("resolved_parent") or n.get("parent")
        if parent:
            i += 1
            edges.append(
                {
                    "id": f"rel-{i:06d}",
                    "from": parent,
                    "to": b,
                    "edge_type": "existing_plan_parent",
                    "classification": (
                        "executable" if st in EXECUTABLE else "triage_only"
                    ),
                    "confidence": "high" if st == "safe" else "medium",
                    "root_branch": n.get("root_branch"),
                    "evidence": [n.get("reason") or "derived from existing analysis"],
                    "metadata": {},
                }
            )
        if st in BLOCKED:
            i += 1
            edges.append(
                {
                    "id": f"rel-{i:06d}",
                    "from": n.get("root_branch"),
                    "to": b,
                    "edge_type": st,
                    "classification": (
                        "blocked" if st != "manual_triage" else "triage_only"
                    ),
                    "confidence": "medium",
                    "root_branch": n.get("root_branch"),
                    "evidence": [n.get("reason") or st],
                    "metadata": {},
                }
            )
    return {"edges": edges}
