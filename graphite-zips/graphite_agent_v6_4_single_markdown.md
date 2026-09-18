# Graphite Multi-Root Agentic Retrofit — V6.4 Single Markdown Inspection Bundle

This single Markdown file contains the V6.4 documentation and runnable scripts in one place for LLM/agentic review.

V6.4 merges the strict **V5.3 Topology Audit Engine** into the V6 evidence/artefact architecture.

---

## 1. Capabilities implemented

V6.4 includes:

- distance-based root ownership with ambiguity detection
- rotation/orientation canonical cycle detection
- DFS cycle discovery
- Kahn topological validation
- parent-exists invariant
- lineage-clear invariant
- patch-unique invariant
- sibling-scoped patch-ID ghost detection
- merge analysis audit for known PR, trunk update, and foreign DAG merges
- `status_audit.json` output
- compact `relationship_graph.json`, `execution_plan.json`, and `triage_packets.json`
- strict post-action verification after Graphite operations
- dry-run execution support through `GRAPHITE_DRY_RUN=1`

---

## 2. Expected package layout

```text
.graphite-agent/
├── graphite_agent/
│   ├── __init__.py
│   └── core.py
├── cli/
│   ├── __init__.py
│   ├── analyze.py
│   └── execute.py
├── contracts/
│   ├── analysis_snapshot.contract.json
│   ├── analysis_summary.contract.json
│   ├── execution_plan.contract.json
│   ├── relationship_graph.contract.json
│   ├── status_audit.contract.json
│   └── triage_packets.contract.json
├── docs/
│   └── HANDOFF.md
├── prompts/
│   └── triage_instructions.md
├── tests/
│   └── test_core.py
├── outputs/
├── 1_analyze_and_plan.py
└── 2_strict_executor.py
```

---

## 3. Operating instructions

### Configure trunks

```bash
export GRAPHITE_TRUNK_BRANCHES="main,release/2.0"
```

### Analyse

```bash
python .graphite-agent/1_analyze_and_plan.py
```

### Dry-run execution

```bash
GRAPHITE_DRY_RUN=1 python .graphite-agent/2_strict_executor.py
```

### Real execution

```bash
unset GRAPHITE_DRY_RUN
python .graphite-agent/2_strict_executor.py
```

### Run tests

```bash
python -m unittest discover .graphite-agent/tests
```

---

## 4. V5.3 capability mapping

| V5.3 capability                 | V6.4 implementation                                        |
| ------------------------------- | ---------------------------------------------------------- |
| Distance-based root ownership   | `TopologyAuditEngine.root_ownership()`                     |
| Root ambiguity detection        | equal-distance candidates set `ambiguous=true`             |
| Canonical cycle detection       | `canonicalize_cycle()` and `cycles()`                      |
| Kahn DAG validation             | `kahn()`                                                   |
| Parent exists invariant         | `audit()`                                                  |
| Lineage clear invariant         | `no_ambiguous_lineage`                                     |
| Patch unique invariant          | sibling-scoped `sibling_patch_overlap()`                   |
| Merge analysis                  | `merge_analysis()`                                         |
| `status_audit.json`             | emitted by `Pipeline.run()`                                |
| Strict post-action verification | `execute()` reruns analysis and checks intended invariants |

---

# 5. Source files

## `.graphite-agent/graphite_agent/__init__.py`

```python
__version__ = "6.4.0"
```

---

## `.graphite-agent/graphite_agent/core.py`

```python
import json, os, subprocess, time
from dataclasses import dataclass, field, asdict, is_dataclass
from functools import lru_cache
from collections import defaultdict, deque
from pathlib import Path

EXECUTABLE_EDGE_TYPES = {"declared_pr_base", "declared_base_mismatch", "nearest_same_root_ancestor"}
BLOCKED_EDGE_TYPES = {"cross_root_ancestry", "trunk_update_merge", "foreign_dag_merge", "cycle_edge"}
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
    roots = [x.strip() for x in os.getenv("GRAPHITE_TRUNK_BRANCHES", "main").split(",") if x.strip()] or ["main"]
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
            last = subprocess.run(args, input=input_text, capture_output=True, text=True, env=env)
            if last.returncode == 0 or i == self.retries:
                break
            time.sleep(0.2 * (i + 1))
        if check and last.returncode != 0:
            raise RuntimeError({"command": args, "exit_code": last.returncode, "stdout": last.stdout, "stderr": last.stderr})
        return last.stdout.strip() if last.stdout else ""

    def ref_exists(self, ref):
        return bool(ref and self.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], check=False))

    def resolve(self, ref):
        if not ref:
            return ref
        if self.ref_exists(ref):
            return ref
        remote_ref = f"{self.remote}/{ref}"
        return remote_ref if self.ref_exists(remote_ref) else ref

    @lru_cache(maxsize=None)
    def is_ancestor(self, ancestor, child):
        if not ancestor or not child:
            return False
        return subprocess.run(
            ["git", "merge-base", "--is-ancestor", str(self.resolve(ancestor)), str(self.resolve(child))],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0

    def merge_base(self, left, right):
        out = self.run(["git", "merge-base", str(self.resolve(left)), str(self.resolve(right))], check=False)
        return out or None

    def commit_distance(self, start, end):
        out = self.run(["git", "rev-list", "--count", f"{self.resolve(start)}..{self.resolve(end)}"], check=False)
        return int(out) if out and out.isdigit() else None

    def merge_commits_between(self, root, branch):
        out = self.run(
            ["git", "log", "--merges", "--format=%H%x1f%P%x1f%s", f"{self.resolve(root)}..{self.resolve(branch)}"],
            check=False,
        )
        return out.splitlines() if out else []

    @lru_cache(maxsize=None)
    def patch_ids_between(self, root, branch):
        log = self.run(["git", "log", "-p", f"{self.resolve(root)}..{self.resolve(branch)}"], check=False)
        if not log:
            return frozenset()
        result = subprocess.run(["git", "patch-id"], input=log, capture_output=True, text=True)
        if result.returncode != 0:
            return frozenset()
        return frozenset(line.split()[0] for line in result.stdout.splitlines() if line.strip())

    def checkout(self, branch):
        if subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"]).returncode == 0:
            self.run(["git", "checkout", "-f", branch])
            return
        remote_ref = f"{self.remote}/{branch}"
        if subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/remotes/{remote_ref}"]).returncode == 0:
            self.run(["git", "checkout", "-f", "-b", branch, "--track", remote_ref])
            return
        raise RuntimeError(f"Branch not found: {branch}")

class GitHub:
    def __init__(self, git):
        self.git = git

    def repos(self):
        raw = self.git.run(["gh", "repo", "view", "--json", "owner,name"], check=False)
        if not raw:
            raise RuntimeError("gh repo metadata unavailable")
        data = json.loads(raw)
        return data["owner"]["login"], data["name"]

    def prs(self):
        owner, repo = self.repos()
        prs = []
        after = "null"
        more = True
        while more:
            query = 'query { repository(owner: "%s", name: "%s") { pullRequests(states: OPEN, first: 100, after: %s) { pageInfo { hasNextPage endCursor } nodes { number title url state isDraft headRefName headRefOid baseRefName reviewDecision mergeStateStatus mergeable commits(last: 1) { nodes { commit { oid } } } } } } }' % (
                owner.replace('"', '\\"'),
                repo.replace('"', '\\"'),
                after,
            )
            raw = self.git.run(["gh", "api", "graphql", "-f", f"query={query}"], check=False)
            if not raw:
                raise RuntimeError("Could not fetch PRs")
            payload = json.loads(raw).get("data", {}).get("repository", {}).get("pullRequests", {})
            for p in payload.get("nodes", []):
                prs.append(PR(
                    p.get("number"), p.get("title"), p.get("url"), p["headRefName"], p.get("headRefOid"), p.get("baseRefName"),
                    p.get("isDraft", False), p.get("reviewDecision"), p.get("mergeStateStatus"), p.get("mergeable"), p,
                ))
            page_info = payload.get("pageInfo", {})
            more = page_info.get("hasNextPage", False)
            after = '"%s"' % page_info.get("endCursor") if more else after
        return prs

class Policy:
    def executable(self, edge):
        return edge.classification == "executable" and edge.edge_type in EXECUTABLE_EDGE_TYPES

    def blocked(self, edge):
        return edge.classification == "blocked" or edge.edge_type in BLOCKED_EDGE_TYPES

    def can_execute(self, node):
        inv = node.audit.invariants
        return node.status in EXECUTABLE_STATUSES and bool(node.resolved_parent) and all(
            inv.get(k) is True for k in [
                "single_root_owner", "no_cycles", "parent_exists", "no_ambiguous_lineage", "no_patch_overlap", "topological_valid"
            ]
        )

class RelationshipCollector:
    def __init__(self, cfg, git, ids):
        self.cfg = cfg
        self.git = git
        self.ids = ids

    def is_root(self, branch):
        return bool(branch and branch in self.cfg.configured_roots)

    def owner(self, branch):
        owners = [r for r in self.cfg.configured_roots if self.git.is_ancestor(r, branch)]
        return owners[0] if len(owners) == 1 else None

    def edge(self, a, b, edge_type, classification, status, confidence, evidence, root=None):
        return Edge(self.ids.rel(), a, b, edge_type, classification, status, confidence, root, evidence)

    def collect(self, prs):
        branch_map = {p.head_ref_name: p for p in prs}
        edges = []
        for p in prs:
            branch = p.head_ref_name
            base = p.base_ref_name
            if self.is_root(branch):
                continue
            root = self.owner(branch) or (base if self.is_root(base) else None)
            if base and (base in branch_map or self.is_root(base)):
                base_root = base if self.is_root(base) else self.owner(base)
                if root and root == base_root and self.git.is_ancestor(base, branch):
                    edges.append(self.edge(base, branch, "declared_pr_base", "executable", "executable", "high", [f"{base} ancestor of {branch}"], root))
                elif root and root == base_root:
                    edges.append(self.edge(base, branch, "declared_base_mismatch", "executable", "needs_restack", "medium", [f"{base} not ancestor of {branch}"], root))
                else:
                    edges.append(self.edge(base, branch, "declared_base_mismatch", "triage_only", "triage_only", "medium", ["base not same root"], root))
            owners = [r for r in self.cfg.configured_roots if self.git.is_ancestor(r, branch)]
            if len(owners) > 1:
                for owner in owners:
                    edges.append(self.edge(owner, branch, "cross_root_ancestry", "blocked", "blocked", "high", [f"{owner} ancestor of {branch}"]))
            if root:
                for line in self.git.merge_commits_between(root, branch):
                    parts = line.split("\x1f")
                    if len(parts) < 3:
                        continue
                    sha, parents, subject = parts[0], parts[1].split(), parts[2]
                    for parent_sha in parents[1:]:
                        known = next((name for name, pr in branch_map.items() if pr.head_ref_oid == parent_sha), None)
                        if known:
                            edges.append(self.edge(known, branch, "known_pr_merge", "triage_only", "triage_only", "medium", [sha, subject], root))
                        elif self.git.is_ancestor(parent_sha, root):
                            edges.append(self.edge(root, branch, "trunk_update_merge", "blocked", "blocked", "high", [sha, subject], root))
                        else:
                            edges.append(self.edge(parent_sha, branch, "foreign_dag_merge", "blocked", "blocked", "high", [sha, subject], root))
        branches = [p.head_ref_name for p in prs if not self.is_root(p.head_ref_name)]
        for i, a in enumerate(branches):
            root_a = self.owner(a)
            if not root_a:
                continue
            for b in branches[i + 1:]:
                if self.owner(b) != root_a:
                    continue
                overlap = self.git.patch_ids_between(root_a, a) & self.git.patch_ids_between(root_a, b)
                if overlap:
                    edges.append(self.edge(a, b, "patch_id_overlap", "triage_only", "triage_only", "medium", [f"shared patch-id count={len(overlap)}"], root_a))
        return edges

class TopologyAuditEngine:
    def __init__(self, cfg, git, policy):
        self.cfg = cfg
        self.git = git
        self.policy = policy

    def root_ownership(self, branch):
        candidates = []
        for root in self.cfg.configured_roots:
            merge_base = self.git.merge_base(root, branch)
            if not merge_base:
                continue
            distance = self.git.commit_distance(merge_base, branch)
            if distance is not None:
                candidates.append({"root": root, "distance": distance, "merge_base": merge_base})
        candidates.sort(key=lambda x: x["distance"])
        ambiguous = len(candidates) > 1 and candidates[0]["distance"] == candidates[1]["distance"]
        owner = None if not candidates or ambiguous else candidates[0]["root"]
        return {"owner": owner, "selected": owner, "candidates": candidates, "ambiguous": ambiguous}

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
                    c = self.canonicalize_cycle(path[path.index(nb):])
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
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
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

    def sibling_patch_overlap(self, branch, root, byroot):
        if not root:
            return False
        mine = self.git.patch_ids_between(root, branch)
        return any(sibling != branch and bool(mine & self.git.patch_ids_between(root, sibling)) for sibling in byroot.get(root, []))

    def merge_analysis(self, branch, edges):
        inbound = [e for e in edges if e.to_ref == branch]
        return {
            "known_pr_merges": [e.from_ref for e in inbound if e.edge_type == "known_pr_merge"],
            "foreign_dag_merges": [e.from_ref for e in inbound if e.edge_type == "foreign_dag_merge"],
            "trunk_updates": [e.from_ref for e in inbound if e.edge_type == "trunk_update_merge"],
        }

    def audit(self, branch, parent, branch_map, root_owner, cycle_path, topo_valid, ambiguous, ghost, edges):
        invariants = {
            "single_root_owner": root_owner["owner"] is not None and not root_owner["ambiguous"],
            "no_cycles": not bool(cycle_path),
            "parent_exists": bool(parent and (parent in branch_map or parent in self.cfg.configured_roots)),
            "no_ambiguous_lineage": not ambiguous,
            "no_patch_overlap": not ghost,
            "topological_valid": topo_valid,
        }
        failed = [k for k, v in invariants.items() if not v]
        return Audit(root_owner, invariants, failed, failed, cycle_path, self.merge_analysis(branch, edges))

class Classifier:
    def __init__(self, policy):
        self.policy = policy

    def classify(self, pr, edges, audit, topo):
        branch = pr.head_ref_name
        branch_edges = [e for e in edges if e.from_ref == branch or e.to_ref == branch]
        inbound = [e for e in edges if e.to_ref == branch]
        executable = [e for e in inbound if self.policy.executable(e)]
        blocked = [e for e in branch_edges if self.policy.blocked(e)]
        known = [e for e in inbound if e.edge_type == "known_pr_merge"]
        parent = executable[0].from_ref if executable else None
        root = executable[0].root_branch if executable else audit.root_owner.get("owner")

        if not audit.invariants["single_root_owner"]:
            status, reason = "cross_root_conflict", "distance root ownership ambiguous or missing"
        elif not audit.invariants["no_cycles"]:
            status, reason = "cycle", "canonical cycle detected"
        elif not audit.invariants["topological_valid"]:
            status, reason = "topology_invalid", "Kahn topological validation failed"
        elif not audit.invariants["no_patch_overlap"]:
            status, reason = "ghost_commit_overlap", "sibling patch-id overlap detected"
        elif blocked:
            status, reason = "blocked_merge_commits", "trunk or foreign merge evidence detected"
        elif len(topo.get("sources", [])) > 1 and len(topo.get("targets", [])) > 1:
            status, reason = "complex_hub_node", "multiple sources and targets"
        elif known and not executable:
            status, reason = "complex_dag_dependency", "known PR merge dependency requires linearisation"
        elif not audit.invariants["parent_exists"]:
            status, reason = "manual_triage", "intended parent missing"
        elif not audit.invariants["no_ambiguous_lineage"]:
            status, reason = "ambiguous_merge_topology", "ambiguous lineage"
        elif executable:
            status, reason = ("needs_restack", "same-root parent but stale ancestry") if executable[0].status == "needs_restack" else ("safe", "all invariants passed")
        else:
            status, reason = "manual_triage", "no executable parent edge"

        risks = []
        if pr.merge_state_status:
            risks.append({
                "type": "failed_ci" if pr.merge_state_status in FAILED_CI_STATES else "mergeability_state",
                "classification": "informational",
                "evidence": [f"mergeStateStatus={pr.merge_state_status}"],
            })

        return Node(
            branch,
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

    def norm(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, list):
            return [self.norm(x) for x in obj]
        if isinstance(obj, dict):
            return {k: self.norm(v) for k, v in obj.items()}
        return obj

    def write(self, name, obj):
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / name).write_text(json.dumps(self.norm(obj), indent=2, sort_keys=True), encoding="utf-8")

class Pipeline:
    def __init__(self, cfg, git=None, prs=None):
        self.cfg = cfg
        self.git = git or Git(cfg.primary_remote, cfg.cli_retries)
        self.ids = Ids()
        self.policy = Policy()
        self.prs_override = prs

    def run(self):
        prs = self.prs_override if self.prs_override is not None else GitHub(self.git).prs()
        branch_map = {p.head_ref_name: p for p in prs}
        edges = RelationshipCollector(self.cfg, self.git, self.ids).collect(prs)
        audit_engine = TopologyAuditEngine(self.cfg, self.git, self.policy)
        graph, pairs, graph_nodes = audit_engine.graph(edges)
        cycles = audit_engine.cycles(graph)
        topo_valid, topo_order = audit_engine.kahn(graph_nodes, pairs)
        topology = self.topology(edges)
        roots = {b: audit_engine.root_ownership(b) for b in branch_map}
        byroot = defaultdict(list)
        for b, ro in roots.items():
            if ro["owner"]:
                byroot[ro["owner"]].append(b)

        nodes = {}
        classifier = Classifier(self.policy)
        for p in prs:
            branch = p.head_ref_name
            if branch in self.cfg.configured_roots:
                continue
            inbound = [e for e in edges if e.to_ref == branch and self.policy.executable(e)]
            parent = inbound[0].from_ref if inbound else None
            topo = topology.get(branch, {"sources": [], "targets": []})
            ghost = audit_engine.sibling_patch_overlap(branch, roots[branch]["owner"], byroot)
            ambiguous = len(topo["sources"]) > 1 and not parent
            audit = audit_engine.audit(branch, parent, branch_map, roots[branch], cycles.get(branch, []), topo_valid, ambiguous, ghost, edges)
            nodes[branch] = classifier.classify(p, edges, audit, topo)

        plan = self.plan(nodes)
        triage = self.triage(nodes)
        lookup = self.lookup(nodes)
        summary = self.summary(nodes, lookup)
        relationship_graph = {"schema_version": self.cfg.schema_version, "edges": edges}
        snapshot = {
            "schema_version": self.cfg.schema_version,
            "metadata": {"configured_roots": self.cfg.configured_roots, "default_root": self.cfg.default_root},
            "pr_catalog": {p.head_ref_name: p.raw for p in prs},
            "branch_graph": {
                "nodes": nodes,
                "edges": [{"from": n.resolved_parent, "to": b, "status": n.status} for b, n in nodes.items() if n.resolved_parent],
                "topo_valid": topo_valid,
                "topo_order": topo_order,
            },
            "relationship_graph": relationship_graph,
            "lookup_tables": lookup,
            "detail_refs": {b: {"branch_node_ref": "/branch_graph/nodes/" + b.replace("/", "~1")} for b in nodes},
            "summary_index": summary,
        }
        writer = Writer(self.cfg.output_dir)
        writer.write("analysis_snapshot.json", snapshot)
        writer.write("status_audit.json", snapshot)
        writer.write("relationship_graph.json", relationship_graph)
        writer.write("analysis_summary.json", summary)
        writer.write("execution_plan.json", plan)
        writer.write("triage_packets.json", triage)
        return snapshot

    def topology(self, edges):
        t = defaultdict(lambda: {"sources": [], "targets": []})
        for e in edges:
            if e.edge_type in {"declared_pr_base", "declared_base_mismatch", "nearest_same_root_ancestor", "known_pr_merge"}:
                if e.from_ref not in t[e.to_ref]["sources"]:
                    t[e.to_ref]["sources"].append(e.from_ref)
                if e.to_ref not in t[e.from_ref]["targets"]:
                    t[e.from_ref]["targets"].append(e.to_ref)
        return t

    def plan(self, nodes):
        queue = []
        for b, n in nodes.items():
            if self.policy.can_execute(n):
                queue.append({
                    "id": self.ids.exec(),
                    "branch": b,
                    "resolved_parent": n.resolved_parent,
                    "root_branch": n.root_branch,
                    "status": n.status,
                    "action": "track_and_restack" if n.status == "needs_restack" else "track_only",
                    "relationship_edges": n.relationship_edges,
                    "preconditions": n.audit.invariants,
                    "intended_topology": {"root": n.root_branch, "parent": n.resolved_parent, "status": n.status, "invariants": n.audit.invariants},
                })
        return {"schema_version": self.cfg.schema_version, "execution_queue": queue}

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
        status = defaultdict(list)
        for b, n in nodes.items():
            status[n.status].append(b)
        return {
            "branch_to_parent": {b: n.resolved_parent for b, n in nodes.items() if n.resolved_parent},
            "branch_to_root": {b: n.root_branch for b, n in nodes.items()},
            "status_to_branches": dict(status),
        }

    def summary(self, nodes, lookup):
        return {
            "schema_version": self.cfg.schema_version,
            "counts": {
                "branches_total": len(nodes),
                "execution_candidates": len([n for n in nodes.values() if n.status in EXECUTABLE_STATUSES]),
                "manual_triage": len([n for n in nodes.values() if n.status not in EXECUTABLE_STATUSES]),
            },
            "by_status": {k: len(v) for k, v in lookup["status_to_branches"].items()},
            "indexes": lookup["status_to_branches"],
        }

class GraphiteClient:
    def __init__(self, git, dry_run=False):
        self.git = git
        self.dry_run = dry_run

    def checkout(self, branch):
        if self.dry_run:
            print("[DRY-RUN] git checkout -f " + branch)
        else:
            self.git.checkout(branch)

    def track(self, branch, parent):
        cmd = ["gt", "track", branch, "--parent", parent, "--force", "--no-interactive"]
        if self.dry_run:
            print("[DRY-RUN] " + " ".join(cmd))
        else:
            self.git.run(cmd)

    def restack(self):
        if self.dry_run:
            print("[DRY-RUN] gt restack --no-interactive")
        else:
            self.git.run(["gt", "restack", "--no-interactive"])

    def verify_parent(self, branch, parent):
        if self.dry_run:
            return True
        out = self.git.run(["gt", "branch", "info", branch, "--no-interactive"])
        actual = None
        for line in out.splitlines():
            if line.strip().startswith("Parent:"):
                actual = line.split(":", 1)[1].strip()
        if actual != parent:
            raise RuntimeError(f"Graphite parent mismatch for {branch}: expected {parent}, got {actual}")
        return True

def build_pipeline():
    return Pipeline(load_config())

def analyse():
    return build_pipeline().run()

def execute():
    cfg = load_config()
    git = Git(cfg.primary_remote, cfg.cli_retries)
    graphite = GraphiteClient(git, cfg.dry_run)
    plan = json.loads((Path(cfg.output_dir) / "execution_plan.json").read_text())
    for step in plan.get("execution_queue", []):
        graphite.checkout(step["branch"])
        graphite.track(step["branch"], step["resolved_parent"])
        if step["action"] == "track_and_restack":
            graphite.restack()
        graphite.verify_parent(step["branch"], step["resolved_parent"])
        if not cfg.dry_run:
            snap = build_pipeline().run()
            node = snap["branch_graph"]["nodes"].get(step["branch"])
            inv = node["audit"]["invariants"] if isinstance(node, dict) else node.audit.invariants
            intended = step["intended_topology"]
            assert inv.get("no_cycles") == intended["invariants"].get("no_cycles")
            assert inv.get("no_ambiguous_lineage") == intended["invariants"].get("no_ambiguous_lineage")
```

---

## `.graphite-agent/cli/analyze.py`

```python
from graphite_agent.core import analyse

def main():
    analyse()

if __name__ == "__main__":
    main()
```

---

## `.graphite-agent/cli/execute.py`

```python
from graphite_agent.core import execute

def main():
    execute()

if __name__ == "__main__":
    main()
```

---

## `.graphite-agent/1_analyze_and_plan.py`

```python
from cli.analyze import main

if __name__ == "__main__":
    main()
```

---

## `.graphite-agent/2_strict_executor.py`

```python
from cli.execute import main

if __name__ == "__main__":
    main()
```

---

## `.graphite-agent/tests/test_core.py`

```python
import unittest, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from graphite_agent.core import TopologyAuditEngine, Config, Policy

class G:
    pass

class T(unittest.TestCase):
    def test_cycle_canonical(self):
        engine = TopologyAuditEngine(Config(["main"], "main"), G(), Policy())
        self.assertEqual(engine.canonicalize_cycle(["b", "a", "c"]), ["a", "b", "c"])

    def test_kahn_invalid(self):
        engine = TopologyAuditEngine(Config(["main"], "main"), G(), Policy())
        ok, _ = engine.kahn(["a", "b"], [("a", "b"), ("b", "a")])
        self.assertFalse(ok)

if __name__ == "__main__":
    unittest.main()
```

---

## `.graphite-agent/prompts/triage_instructions.md`

```markdown
# Triage SOPs

Use the audit invariants to select SOPs. Do not improvise.

- Cross-root conflict: ask the user for the correct root and rebase under that root.
- Cycle: identify and remove the loop-closing commit.
- Hub node: flatten or extract a shared base.
- PR DAG dependency: linearise by rebasing onto the known PR dependency.
- Blocked merge: strip trunk or foreign DAG merge history.
```

---

## `.graphite-agent/docs/HANDOFF.md`

```markdown
# V6.4 Handoff

This package merges V5.3 strict audit semantics into the V6 evidence and artefact model.

Execution is only allowed when all authoritative invariants pass:

- `single_root_owner`
- `no_cycles`
- `parent_exists`
- `no_ambiguous_lineage`
- `no_patch_overlap`
- `topological_valid`

The pipeline emits:

- `analysis_snapshot.json`
- `status_audit.json`
- `relationship_graph.json`
- `analysis_summary.json`
- `execution_plan.json`
- `triage_packets.json`
```

---

## 6. Minimal JSON contracts

### `.graphite-agent/contracts/analysis_snapshot.contract.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object"
}
```

### `.graphite-agent/contracts/status_audit.contract.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object"
}
```

### `.graphite-agent/contracts/execution_plan.contract.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object"
}
```

---

## 7. Review notes for an inspecting LLM

Important things to inspect:

1. `TopologyAuditEngine.root_ownership()` for V5.3-style distance root ownership.
2. `TopologyAuditEngine.canonicalize_cycle()` for rotation/orientation normalisation.
3. `TopologyAuditEngine.kahn()` for global DAG validity.
4. `TopologyAuditEngine.sibling_patch_overlap()` for same-root sibling ghost detection.
5. `Policy.can_execute()` for strict invariant-gated execution.
6. `Pipeline.run()` for artefact generation.
7. `execute()` for post-action verification.

Known limitations to evaluate:

- JSON contracts are minimal and can be made stricter.
- The implementation expects real `git`, authenticated `gh`, and `gt` CLIs.
- The post-action verification checks the most critical invariants but can be expanded to compare the full audit object.
- Large repositories may still benefit from persistent on-disk caching beyond in-process LRU.
