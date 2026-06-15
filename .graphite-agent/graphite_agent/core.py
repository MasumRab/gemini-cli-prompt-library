import json, os, subprocess, time
from dataclasses import dataclass, field, asdict, is_dataclass
from functools import lru_cache
from collections import defaultdict, deque
from pathlib import Path

EXECUTABLE_EDGE_TYPES = {
    "declared_pr_base",
    "declared_base_mismatch",
    "nearest_same_root_ancestor",
}
BLOCKED_EDGE_TYPES = {
    "cross_root_ancestry",
    "trunk_update_merge",
    "foreign_dag_merge",
    "cycle_edge",
}
EXECUTABLE_STATUSES = {"safe", "needs_restack"}
FAILED_CI_STATES = {"BLOCKED", "DIRTY", "UNKNOWN", "UNSTABLE", "FAILURE", "ERROR"}


@dataclass
class Config:
    configured_roots: list[str]
    default_root: str
    primary_remote: str = "origin"
    output_dir: str = ".graphite-agent/outputs"
    schema_version: str = "6.4"
    dry_run: bool = False
    cli_retries: int = 2


def load_config():
    roots = [
        x.strip()
        for x in os.getenv("GRAPHITE_TRUNK_BRANCHES", "main").split(",")
        if x.strip()
    ] or ["main"]
    return Config(
        roots,
        roots[0],
        os.getenv("GRAPHITE_PRIMARY_REMOTE", "origin"),
        os.getenv("GRAPHITE_AGENT_OUTPUT_DIR", ".graphite-agent/outputs"),
        os.getenv("GRAPHITE_AGENT_SCHEMA_VERSION", "6.4"),
        os.getenv("GRAPHITE_DRY_RUN", "0") == "1",
        int(os.getenv("GRAPHITE_CLI_RETRIES", "2")),
    )


@dataclass
class PR:
    number: int | None
    title: str | None
    url: str | None
    head_ref_name: str
    head_ref_oid: str | None
    base_ref_name: str | None
    is_draft: bool = False
    review_decision: str | None = None
    merge_state_status: str | None = None
    mergeable: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass
class Edge:
    id: str
    from_ref: str
    to_ref: str
    edge_type: str
    classification: str
    status: str
    confidence: str
    root_branch: str | None
    evidence: list[str]


@dataclass
class Audit:
    root_owner: dict
    invariants: dict
    failed_invariants: list
    triage_reason: list
    cycle_path: list = field(default_factory=list)
    merge_analysis: dict = field(default_factory=dict)


@dataclass
class Node:
    branch: str
    root_branch: str | None
    resolved_parent: str | None
    status: str
    reason: str
    audit: Audit
    relationship_edges: list[str]
    sources: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    risk_annotations: list[dict] = field(default_factory=list)


class Ids:
    def __init__(self):
        self.r = 0
        self.t = 0
        self.e = 0

    def rel(self):
        self.r += 1
        return f"rel-{self.r:06d}"

    def triage(self):
        self.t += 1
        return f"triage-{self.t:06d}"

    def exec(self):
        self.e += 1
        return f"exec-{self.e:06d}"


class Git:
    def __init__(self, remote="origin", retries=2):
        self.remote = remote
        self.retries = retries

    def run(self, args, check=True, input_text=None):
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GRAPHITE_NO_INTERACTIVE"] = "1"
        last = None
        for i in range(max(1, self.retries + 1)):
            last = # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    subprocess.run(
                args, input=input_text, capture_output=True, text=True, env=env
            )
            if last.returncode == 0 or i == self.retries:
                break
            time.sleep(0.2 * (i + 1))
        if check and last.returncode != 0:
            raise RuntimeError(
                {
                    "command": args,
                    "exit_code": last.returncode,
                    "stdout": last.stdout,
                    "stderr": last.stderr,
                }
            )
        return last.stdout.strip() if last.stdout else ""

    def ref_exists(self, ref):
        return bool(
            ref
            and self.run(
                ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], check=False
            )
        )

    def resolve(self, ref):
        if not ref:
            return ref
        if self.ref_exists(ref):
            return ref
        rr = f"{self.remote}/{ref}"
        return rr if self.ref_exists(rr) else ref

    @lru_cache(maxsize=None)
    def is_ancestor(self, a, b):
        if not a or not b:
            return False
        return (
            # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    subprocess.run(
                [
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    str(self.resolve(a)),
                    str(self.resolve(b)),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )

    def merge_base(self, a, b):
        out = self.run(
            ["git", "merge-base", str(self.resolve(a)), str(self.resolve(b))],
            check=False,
        )
        return out or None

    def commit_distance(self, a, b):
        out = self.run(
            ["git", "rev-list", "--count", f"{self.resolve(a)}..{self.resolve(b)}"],
            check=False,
        )
        return int(out) if out and out.isdigit() else None

    def merge_commits_between(self, root, branch):
        out = self.run(
            [
                "git",
                "log",
                "--merges",
                "--format=%H%x1f%P%x1f%s",
                f"{self.resolve(root)}..{self.resolve(branch)}",
            ],
            check=False,
        )
        return out.splitlines() if out else []

    @lru_cache(maxsize=None)
    def patch_ids_between(self, root, branch):
        log = self.run(
            ["git", "log", "-p", f"{self.resolve(root)}..{self.resolve(branch)}"],
            check=False,
        )
        if not log:
            return frozenset()
        r = # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    subprocess.run(
            ["git", "patch-id"], input=log, capture_output=True, text=True
        )
        return (
            frozenset(x.split()[0] for x in r.stdout.splitlines() if x.strip())
            if r.returncode == 0
            else frozenset()
        )

    def checkout(self, b):
        if (
            # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{b}"]
            ).returncode
            == 0
        ):
            self.run(["git", "checkout", "-f", b])
            return
        rb = f"{self.remote}/{b}"
        if (
            # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/remotes/{rb}"]
            ).returncode
            == 0
        ):
            self.run(["git", "checkout", "-f", "-b", b, "--track", rb])
            return
        raise RuntimeError(f"Branch not found: {b}")


class GitHub:
    def __init__(self, git):
        self.git = git

    def repos(self):
        raw = self.git.run(["gh", "repo", "view", "--json", "owner,name"], check=False)
        if not raw:
            raise RuntimeError("gh repo metadata unavailable")
        d = json.loads(raw)
        return d["owner"]["login"], d["name"]

    def prs(self):
        owner, repo = self.repos()
        prs = []
        after = "null"
        more = True
        while more:
            q = (
                'query { repository(owner: "%s", name: "%s") { pullRequests(states: OPEN, first: 100, after: %s) { pageInfo { hasNextPage endCursor } nodes { number title url state isDraft headRefName headRefOid baseRefName reviewDecision mergeStateStatus mergeable commits(last: 1) { nodes { commit { oid } } } } } } }'
                % (owner.replace('"', '\\"'), repo.replace('"', '\\"'), after)
            )
            raw = self.git.run(
                ["gh", "api", "graphql", "-f", f"query={q}"], check=False
            )
            if not raw:
                raise RuntimeError("Could not fetch PRs")
            pd = (
                json.loads(raw)
                .get("data", {})
                .get("repository", {})
                .get("pullRequests", {})
            )
            for p in pd.get("nodes", []):
                prs.append(
                    PR(
                        p.get("number"),
                        p.get("title"),
                        p.get("url"),
                        p["headRefName"],
                        p.get("headRefOid"),
                        p.get("baseRefName"),
                        p.get("isDraft", False),
                        p.get("reviewDecision"),
                        p.get("mergeStateStatus"),
                        p.get("mergeable"),
                        p,
                    )
                )
            pi = pd.get("pageInfo", {})
            more = pi.get("hasNextPage", False)
            after = '"%s"' % pi.get("endCursor") if more else after
        return prs


class Policy:
    def executable(self, e):
        return e.classification == "executable" and e.edge_type in EXECUTABLE_EDGE_TYPES

    def blocked(self, e):
        return e.classification == "blocked" or e.edge_type in BLOCKED_EDGE_TYPES

    def can_execute(self, n):
        inv = n.audit.invariants
        return (
            n.status in EXECUTABLE_STATUSES
            and bool(n.resolved_parent)
            and all(
                inv.get(k) is True
                for k in [
                    "single_root_owner",
                    "no_cycles",
                    "parent_exists",
                    "no_ambiguous_lineage",
                    "no_patch_overlap",
                    "topological_valid",
                ]
            )
        )


class RelationshipCollector:
    def __init__(self, cfg, git, ids):
        self.cfg = cfg
        self.git = git
        self.ids = ids

    def is_root(self, b):
        return bool(b and b in self.cfg.configured_roots)

    def owner(self, b):
        owners = [r for r in self.cfg.configured_roots if self.git.is_ancestor(r, b)]
        return owners[0] if len(owners) == 1 else None

    def edge(self, a, b, t, c, s, conf, ev, root=None):
        return Edge(self.ids.rel(), a, b, t, c, s, conf, root, ev)

    def collect(self, prs):
        bm = {p.head_ref_name: p for p in prs}
        edges = []
        for p in prs:
            b = p.head_ref_name
            base = p.base_ref_name
            if self.is_root(b):
                continue
            root = self.owner(b) or (base if self.is_root(base) else None)
            if base and (base in bm or self.is_root(base)):
                base_root = base if self.is_root(base) else self.owner(base)
                if root and root == base_root and self.git.is_ancestor(base, b):
                    edges.append(
                        self.edge(
                            base,
                            b,
                            "declared_pr_base",
                            "executable",
                            "executable",
                            "high",
                            [f"{base} ancestor of {b}"],
                            root,
                        )
                    )
                elif root and root == base_root:
                    edges.append(
                        self.edge(
                            base,
                            b,
                            "declared_base_mismatch",
                            "executable",
                            "needs_restack",
                            "medium",
                            [f"{base} not ancestor of {b}"],
                            root,
                        )
                    )
                else:
                    edges.append(
                        self.edge(
                            base,
                            b,
                            "declared_base_mismatch",
                            "triage_only",
                            "triage_only",
                            "medium",
                            ["base not same root"],
                            root,
                        )
                    )
            owners = [
                r for r in self.cfg.configured_roots if self.git.is_ancestor(r, b)
            ]
            if len(owners) > 1:
                for o in owners:
                    edges.append(
                        self.edge(
                            o,
                            b,
                            "cross_root_ancestry",
                            "blocked",
                            "blocked",
                            "high",
                            [f"{o} ancestor of {b}"],
                        )
                    )
            if root:
                for line in self.git.merge_commits_between(root, b):
                    parts = line.split("\x1f")
                    if len(parts) < 3:
                        continue
                    sha, parents, subj = parts[0], parts[1].split(), parts[2]
                    for psha in parents[1:]:
                        known = next(
                            (n for n, pr in bm.items() if pr.head_ref_oid == psha), None
                        )
                        if known:
                            edges.append(
                                self.edge(
                                    known,
                                    b,
                                    "known_pr_merge",
                                    "triage_only",
                                    "triage_only",
                                    "medium",
                                    [sha, subj],
                                    root,
                                )
                            )
                        elif self.git.is_ancestor(psha, root):
                            edges.append(
                                self.edge(
                                    root,
                                    b,
                                    "trunk_update_merge",
                                    "blocked",
                                    "blocked",
                                    "high",
                                    [sha, subj],
                                    root,
                                )
                            )
                        else:
                            edges.append(
                                self.edge(
                                    psha,
                                    b,
                                    "foreign_dag_merge",
                                    "blocked",
                                    "blocked",
                                    "high",
                                    [sha, subj],
                                    root,
                                )
                            )
        branches = [p.head_ref_name for p in prs if not self.is_root(p.head_ref_name)]
        for i, a in enumerate(branches):
            ra = self.owner(a)
            if not ra:
                continue
            for b in branches[i + 1 :]:
                if self.owner(b) != ra:
                    continue
                ov = self.git.patch_ids_between(ra, a) & self.git.patch_ids_between(
                    ra, b
                )
                if ov:
                    edges.append(
                        self.edge(
                            a,
                            b,
                            "patch_id_overlap",
                            "triage_only",
                            "triage_only",
                            "medium",
                            [f"shared patch-id count={len(ov)}"],
                            ra,
                        )
                    )
        return edges


class TopologyAuditEngine:
    def __init__(self, cfg, git, policy):
        self.cfg = cfg
        self.git = git
        self.policy = policy

    def root_ownership(self, b):
        cand = []
        for r in self.cfg.configured_roots:
            mb = self.git.merge_base(r, b)
            if not mb:
                continue
            d = self.git.commit_distance(mb, b)
            if d is not None:
                cand.append({"root": r, "distance": d, "merge_base": mb})
        cand.sort(key=lambda x: x["distance"])
        amb = len(cand) > 1 and cand[0]["distance"] == cand[1]["distance"]
        owner = None if not cand or amb else cand[0]["root"]
        return {"owner": owner, "selected": owner, "candidates": cand, "ambiguous": amb}

    def canonicalize_cycle(self, cycle):
        if not cycle:
            return []

        def rot(c):
            i = c.index(min(c))
            return tuple(c[i:] + c[:i])

        return list(min(rot(cycle), rot(list(reversed(cycle)))))

    def cycles(self, graph):
        visited = set()
        stack = set()
        path = []
        cycles = {}

        def dfs(n):
            visited.add(n)
            stack.add(n)
            path.append(n)
            for nb in graph.get(n, []):
                if nb not in visited:
                    dfs(nb)
                elif nb in stack:
                    c = self.canonicalize_cycle(path[path.index(nb) :])
                    for x in c:
                        cycles[x] = c
            stack.discard(n)
            path.pop()

        for n in list(graph):
            if n not in visited:
                dfs(n)
        return cycles

    def kahn(self, nodes, edges):
        indeg = {n: 0 for n in nodes}
        adj = defaultdict(list)
        for a, b in edges:
            indeg.setdefault(a, 0)
            indeg.setdefault(b, 0)
            indeg[b] += 1
            adj[a].append(b)
        q = deque([n for n, d in indeg.items() if d == 0])
        out = []
        while q:
            u = q.popleft()
            out.append(u)
            for v in adj.get(u, []):
                indeg.__setitem__(v, indeg[v] - 1)
                q.append(v) if indeg[v] == 0 else None
        return len(out) == len(indeg), out

    def graph(self, edges):
        g = defaultdict(list)
        pairs = []
        nodes = set()
        for e in edges:
            if self.policy.executable(e):
                g[e.from_ref].append(e.to_ref)
                pairs.append((e.from_ref, e.to_ref))
                nodes.update([e.from_ref, e.to_ref])
        return g, pairs, nodes

    def sibling_patch_overlap(self, b, root, byroot):
        if not root:
            return False
        mine = self.git.patch_ids_between(root, b)
        return any(
            s != b and bool(mine & self.git.patch_ids_between(root, s))
            for s in byroot.get(root, [])
        )

    def merge_analysis(self, b, edges):
        inbound = [e for e in edges if e.to_ref == b]
        return {
            "known_pr_merges": [
                e.from_ref for e in inbound if e.edge_type == "known_pr_merge"
            ],
            "foreign_dag_merges": [
                e.from_ref for e in inbound if e.edge_type == "foreign_dag_merge"
            ],
            "trunk_updates": [
                e.from_ref for e in inbound if e.edge_type == "trunk_update_merge"
            ],
        }

    def audit(
        self, b, parent, bm, root_owner, cycle_path, topo_valid, ambiguous, ghost, edges
    ):
        inv = {
            "single_root_owner": root_owner["owner"] is not None
            and not root_owner["ambiguous"],
            "no_cycles": not bool(cycle_path),
            "parent_exists": bool(
                parent and (parent in bm or parent in self.cfg.configured_roots)
            ),
            "no_ambiguous_lineage": not ambiguous,
            "no_patch_overlap": not ghost,
            "topological_valid": topo_valid,
        }
        failed = [k for k, v in inv.items() if not v]
        return Audit(
            root_owner, inv, failed, failed, cycle_path, self.merge_analysis(b, edges)
        )


class Classifier:
    def __init__(self, policy):
        self.policy = policy

    def classify(self, pr, edges, audit, topo):
        b = pr.head_ref_name
        branch_edges = [e for e in edges if e.from_ref == b or e.to_ref == b]
        inbound = [e for e in edges if e.to_ref == b]
        execs = [e for e in inbound if self.policy.executable(e)]
        blocked = [e for e in branch_edges if self.policy.blocked(e)]
        known = [e for e in inbound if e.edge_type == "known_pr_merge"]
        parent = execs[0].from_ref if execs else None
        root = execs[0].root_branch if execs else audit.root_owner.get("owner")
        if not audit.invariants["single_root_owner"]:
            status, reason = (
                "cross_root_conflict",
                "distance root ownership ambiguous or missing",
            )
        elif not audit.invariants["no_cycles"]:
            status, reason = "cycle", "canonical cycle detected"
        elif not audit.invariants["topological_valid"]:
            status, reason = "topology_invalid", "Kahn topological validation failed"
        elif not audit.invariants["no_patch_overlap"]:
            status, reason = "ghost_commit_overlap", "sibling patch-id overlap detected"
        elif blocked:
            status, reason = (
                "blocked_merge_commits",
                "trunk or foreign merge evidence detected",
            )
        elif len(topo.get("sources", [])) > 1 and len(topo.get("targets", [])) > 1:
            status, reason = "complex_hub_node", "multiple sources and targets"
        elif known and not execs:
            status, reason = (
                "complex_dag_dependency",
                "known PR merge dependency requires linearisation",
            )
        elif not audit.invariants["parent_exists"]:
            status, reason = "manual_triage", "intended parent missing"
        elif not audit.invariants["no_ambiguous_lineage"]:
            status, reason = "ambiguous_merge_topology", "ambiguous lineage"
        elif execs:
            status, reason = (
                ("needs_restack", "same-root parent but stale ancestry")
                if execs[0].status == "needs_restack"
                else ("safe", "all invariants passed")
            )
        else:
            status, reason = "manual_triage", "no executable parent edge"
        risks = []
        if pr.merge_state_status:
            risks.append(
                {
                    "type": (
                        "failed_ci"
                        if pr.merge_state_status in FAILED_CI_STATES
                        else "mergeability_state"
                    ),
                    "classification": "informational",
                    "evidence": [f"mergeStateStatus={pr.merge_state_status}"],
                }
            )
        return Node(
            b,
            root,
            parent if status in EXECUTABLE_STATUSES else None,
            status,
            reason,
            audit,
            [e.id for e in branch_edges],
            topo.get("sources", []),
            topo.get("targets", []),
            risks,
        )


class Writer:
    def __init__(self, out):
        self.out = Path(out)

    def norm(self, o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, list):
            return [self.norm(x) for x in o]
        if isinstance(o, dict):
            return {k: self.norm(v) for k, v in o.items()}
        return o

    def write(self, name, obj):
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / name).write_text(
            json.dumps(self.norm(obj), indent=2, sort_keys=True), encoding="utf-8"
        )


class Pipeline:
    def __init__(self, cfg, git=None, prs=None):
        self.cfg = cfg
        self.git = git or Git(cfg.primary_remote, cfg.cli_retries)
        self.ids = Ids()
        self.policy = Policy()
        self.prs_override = prs

    def run(self):
        prs = (
            self.prs_override
            if self.prs_override is not None
            else GitHub(self.git).prs()
        )
        bm = {p.head_ref_name: p for p in prs}
        edges = RelationshipCollector(self.cfg, self.git, self.ids).collect(prs)
        audit_engine = TopologyAuditEngine(self.cfg, self.git, self.policy)
        graph, pairs, gnodes = audit_engine.graph(edges)
        cycles = audit_engine.cycles(graph)
        topo_valid, topo_order = audit_engine.kahn(gnodes, pairs)
        topology = self.topology(edges)
        roots = {b: audit_engine.root_ownership(b) for b in bm}
        byroot = defaultdict(list)
        for b, ro in roots.items():
            if ro["owner"]:
                byroot[ro["owner"]].append(b)
        nodes = {}
        classifier = Classifier(self.policy)
        for p in prs:
            b = p.head_ref_name
            if b in self.cfg.configured_roots:
                continue
            inbound = [e for e in edges if e.to_ref == b and self.policy.executable(e)]
            parent = inbound[0].from_ref if inbound else None
            topo = topology.get(b, {"sources": [], "targets": []})
            ghost = audit_engine.sibling_patch_overlap(b, roots[b]["owner"], byroot)
            ambiguous = len(topo["sources"]) > 1 and not parent
            audit = audit_engine.audit(
                b,
                parent,
                bm,
                roots[b],
                cycles.get(b, []),
                topo_valid,
                ambiguous,
                ghost,
                edges,
            )
            nodes[b] = classifier.classify(p, edges, audit, topo)
        plan = self.plan(nodes)
        triage = self.triage(nodes)
        lookup = self.lookup(nodes)
        summary = self.summary(nodes, lookup)
        rel = {"schema_version": self.cfg.schema_version, "edges": edges}
        snap = {
            "schema_version": self.cfg.schema_version,
            "metadata": {
                "configured_roots": self.cfg.configured_roots,
                "default_root": self.cfg.default_root,
            },
            "pr_catalog": {p.head_ref_name: p.raw for p in prs},
            "branch_graph": {
                "nodes": nodes,
                "edges": [
                    {"from": n.resolved_parent, "to": b, "status": n.status}
                    for b, n in nodes.items()
                    if n.resolved_parent
                ],
                "topo_valid": topo_valid,
                "topo_order": topo_order,
            },
            "relationship_graph": rel,
            "lookup_tables": lookup,
            "detail_refs": {
                b: {"branch_node_ref": "/branch_graph/nodes/" + b.replace("/", "~1")}
                for b in nodes
            },
            "summary_index": summary,
        }
        w = Writer(self.cfg.output_dir)
        w.write("analysis_snapshot.json", snap)
        w.write("status_audit.json", snap)
        w.write("relationship_graph.json", rel)
        w.write("analysis_summary.json", summary)
        w.write("execution_plan.json", plan)
        w.write("triage_packets.json", triage)
        return snap

    def topology(self, edges):
        t = defaultdict(lambda: {"sources": [], "targets": []})
        for e in edges:
            if e.edge_type in {
                "declared_pr_base",
                "declared_base_mismatch",
                "nearest_same_root_ancestor",
                "known_pr_merge",
            }:
                if e.from_ref not in t[e.to_ref]["sources"]:
                    t[e.to_ref]["sources"].append(e.from_ref)
                if e.to_ref not in t[e.from_ref]["targets"]:
                    t[e.from_ref]["targets"].append(e.to_ref)
        return t

    def plan(self, nodes):
        q = []
        for b, n in nodes.items():
            if self.policy.can_execute(n):
                q.append(
                    {
                        "id": self.ids.exec(),
                        "branch": b,
                        "resolved_parent": n.resolved_parent,
                        "root_branch": n.root_branch,
                        "status": n.status,
                        "action": (
                            "track_and_restack"
                            if n.status == "needs_restack"
                            else "track_only"
                        ),
                        "relationship_edges": n.relationship_edges,
                        "preconditions": n.audit.invariants,
                        "intended_topology": {
                            "root": n.root_branch,
                            "parent": n.resolved_parent,
                            "status": n.status,
                            "invariants": n.audit.invariants,
                        },
                    }
                )
        return {"schema_version": self.cfg.schema_version, "execution_queue": q}

    def triage(self, nodes):
        packets = {}
        for b, n in nodes.items():
            if self.policy.can_execute(n):
                continue
            pid = self.ids.triage()
            packets[pid] = {
                "id": pid,
                "branch": b,
                "status": n.status,
                "primary_reason": n.reason,
                "audit": n.audit,
                "relationship_edges": n.relationship_edges,
                "recommended_action": "manual review; use matching SOP",
            }
        return {"schema_version": self.cfg.schema_version, "packets": packets}

    def lookup(self, nodes):
        st = defaultdict(list)
        for b, n in nodes.items():
            st[n.status].append(b)
        return {
            "branch_to_parent": {
                b: n.resolved_parent for b, n in nodes.items() if n.resolved_parent
            },
            "branch_to_root": {b: n.root_branch for b, n in nodes.items()},
            "status_to_branches": dict(st),
        }

    def summary(self, nodes, lookup):
        return {
            "schema_version": self.cfg.schema_version,
            "counts": {
                "branches_total": len(nodes),
                "execution_candidates": len(
                    [n for n in nodes.values() if n.status in EXECUTABLE_STATUSES]
                ),
                "manual_triage": len(
                    [n for n in nodes.values() if n.status not in EXECUTABLE_STATUSES]
                ),
            },
            "by_status": {k: len(v) for k, v in lookup["status_to_branches"].items()},
            "indexes": lookup["status_to_branches"],
        }


class GraphiteClient:
    def __init__(self, git, dry_run=False):
        self.git = git
        self.dry_run = dry_run

    def checkout(self, b):
        (
            print("[DRY-RUN] git checkout -f " + b)
            if self.dry_run
            else self.git.checkout(b)
        )

    def track(self, b, p):
        cmd = ["gt", "track", b, "--parent", p, "--force", "--no-interactive"]
        print("[DRY-RUN] " + " ".join(cmd)) if self.dry_run else self.git.run(cmd)

    def restack(self):
        (
            print("[DRY-RUN] gt restack --no-interactive")
            if self.dry_run
            else self.git.run(["gt", "restack", "--no-interactive"])
        )

    def verify_parent(self, b, p):
        if self.dry_run:
            return True
        out = self.git.run(["gt", "branch", "info", b, "--no-interactive"])
        actual = None
        for line in out.splitlines():
            if line.strip().startswith("Parent:"):
                actual = line.split(":", 1)[1].strip()
        if actual != p:
            raise RuntimeError(
                f"Graphite parent mismatch for {b}: expected {p}, got {actual}"
            )
        return True


def build_pipeline():
    return Pipeline(load_config())


def analyse():
    return build_pipeline().run()


def execute():
    cfg = load_config()
    git = Git(cfg.primary_remote, cfg.cli_retries)
    gc = GraphiteClient(git, cfg.dry_run)
    plan = json.loads((Path(cfg.output_dir) / "execution_plan.json").read_text())
    for step in plan.get("execution_queue", []):
        gc.checkout(step["branch"])
        gc.track(step["branch"], step["resolved_parent"])
        if step["action"] == "track_and_restack":
            gc.restack()
        gc.verify_parent(step["branch"], step["resolved_parent"])
        if not cfg.dry_run:
            snap = build_pipeline().run()
            node = snap["branch_graph"]["nodes"].get(step["branch"])
            inv = (
                node["audit"]["invariants"]
                if isinstance(node, dict)
                else node.audit.invariants
            )
            intended = step["intended_topology"]
            assert inv.get("no_cycles") == intended["invariants"].get("no_cycles")
            assert inv.get("no_ambiguous_lineage") == intended["invariants"].get(
                "no_ambiguous_lineage"
            )
