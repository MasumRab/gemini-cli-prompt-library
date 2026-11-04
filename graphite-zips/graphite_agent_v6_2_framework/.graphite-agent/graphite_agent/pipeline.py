from collections import defaultdict
from datetime import datetime, timezone


class AnalysisPipeline:
    def __init__(
        self,
        config,
        pr_provider,
        relationship_collector,
        classifier,
        plan_compiler,
        artefact_writer,
        policy,
    ):
        self.config = config
        self.pr_provider = pr_provider
        self.relationship_collector = relationship_collector
        self.classifier = classifier
        self.plan_compiler = plan_compiler
        self.artefact_writer = artefact_writer
        self.policy = policy

    def run(self):
        prs = self.pr_provider.list_open_prs()
        pr_catalog = {pr.head_ref_name: pr.raw for pr in prs}
        edges = self.relationship_collector.collect(prs)
        cycle_nodes = self._detect_cycle_nodes(edges)
        nodes = {
            pr.head_ref_name: self.classifier.classify(
                pr, edges, pr.head_ref_name in cycle_nodes
            )
            for pr in prs
            if pr.head_ref_name not in self.config.configured_roots
        }
        relationship_graph = {
            "schema_version": self.config.schema_version,
            "edges": edges,
        }
        branch_graph = {"nodes": nodes, "edges": self._branch_edges(nodes)}
        lookup = self._lookup_tables(nodes)
        refs = self._detail_refs(nodes)
        summary = self._summary(nodes, lookup)
        execution_plan = self.plan_compiler.compile_execution_plan(nodes)
        triage_packets = self.plan_compiler.compile_triage_packets(nodes)
        snapshot = {
            "schema_version": self.config.schema_version,
            "metadata": {
                "configured_roots": self.config.configured_roots,
                "default_root": self.config.default_root,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "pr_catalog": pr_catalog,
            "branch_graph": branch_graph,
            "relationship_graph": relationship_graph,
            "lookup_tables": lookup,
            "detail_refs": refs,
            "summary_index": summary,
            "augmentation": {"modules": {}},
        }
        self.artefact_writer.write_all(
            snapshot, relationship_graph, summary, execution_plan, triage_packets
        )
        return snapshot

    def _detect_cycle_nodes(self, edges):
        adj = defaultdict(list)
        nodes = set()
        for e in edges:
            if self.policy.is_executable_edge(e):
                adj[e.from_ref].append(e.to_ref)
                nodes.update([e.from_ref, e.to_ref])
        visited = set()
        stack = set()
        path = []
        cycle = set()

        def dfs(n):
            visited.add(n)
            stack.add(n)
            path.append(n)
            for c in adj.get(n, []):
                if c not in visited:
                    dfs(c)
                elif c in stack:
                    try:
                        cycle.update(path[path.index(c) :])
                    except ValueError:
                        cycle.add(c)
            stack.discard(n)
            if path and path[-1] == n:
                path.pop()

        for n in list(nodes):
            if n not in visited:
                dfs(n)
        return cycle

    def _branch_edges(self, nodes):
        return [
            {
                "from": n.resolved_parent,
                "to": b,
                "edge_type": "graphite_parent_candidate",
                "status": n.status,
            }
            for b, n in nodes.items()
            if n.status in {"safe", "needs_restack"} and n.resolved_parent
        ]

    def _lookup_tables(self, nodes):
        status = defaultdict(list)
        children = defaultdict(list)
        parent = {}
        for b, n in nodes.items():
            status[n.status].append(b)
            if n.resolved_parent:
                parent[b] = n.resolved_parent
                children[n.resolved_parent].append(b)
        return {
            "branch_to_parent": parent,
            "branch_to_children": dict(children),
            "branch_to_root": {b: n.root_branch for b, n in nodes.items()},
            "status_to_branches": dict(status),
        }

    def _detail_refs(self, nodes):
        return {
            b: {
                "branch_node_ref": f"analysis_snapshot.branch_graph.nodes.{b}",
                "relationship_edges_ref": n.relationship_edges,
                "pr_ref": f"analysis_snapshot.pr_catalog.{b}",
            }
            for b, n in nodes.items()
        }

    def _summary(self, nodes, lookup):
        st = lookup["status_to_branches"]
        by_root = defaultdict(int)
        for n in nodes.values():
            if n.root_branch:
                by_root[n.root_branch] += 1
        return {
            "schema_version": self.config.schema_version,
            "counts": {
                "branches_total": len(nodes),
                "execution_candidates": len(
                    [
                        b
                        for b, n in nodes.items()
                        if n.status in {"safe", "needs_restack"}
                    ]
                ),
                "manual_triage": len(
                    [
                        b
                        for b, n in nodes.items()
                        if n.status not in {"safe", "needs_restack"}
                    ]
                ),
            },
            "by_status": {k: len(v) for k, v in st.items()},
            "by_root": dict(by_root),
            "indexes": {
                "safe_branches": st.get("safe", []),
                "needs_restack_branches": st.get("needs_restack", []),
                "cross_root_branches": st.get("cross_root_conflict", []),
                "merge_blocked_branches": st.get("blocked_merge_commits", []),
                "patch_overlap_branches": st.get("patch_equivalence_only", []),
                "unrooted_branches": st.get("unrooted", []),
                "ambiguous_branches": st.get("ambiguous_relationship", []),
                "failed_ci_branches": [],
            },
        }
