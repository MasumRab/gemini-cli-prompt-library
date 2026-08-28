from .models import RelationshipEdge


class RelationshipCollector:
    def __init__(self, config, git, ids):
        self.config = config
        self.git = git
        self.ids = ids

    def collect(self, prs):
        branch_map = {pr.head_ref_name: pr for pr in prs}
        edges = []
        edges += self._collect_declared_base_edges(prs, branch_map)
        edges += self._collect_nearest_same_root_edges(prs, branch_map, edges)
        edges += self._collect_cross_root_edges(prs)
        edges += self._collect_merge_edges(prs, branch_map)
        edges += self._collect_patch_overlap_edges(prs, branch_map)
        return edges

    def _edge(
        self,
        from_ref,
        to_ref,
        edge_type,
        classification,
        status,
        confidence,
        evidence,
        root_branch=None,
    ):
        return RelationshipEdge(
            self.ids.relationship_id(),
            from_ref,
            to_ref,
            edge_type,
            classification,
            status,
            confidence,
            root_branch,
            evidence,
        )

    def _is_root(self, branch):
        return bool(branch and branch in self.config.configured_roots)

    def root_owners_for_branch(self, branch):
        return [
            r for r in self.config.configured_roots if self.git.is_ancestor(r, branch)
        ]

    def select_root_owner(self, branch, base_ref, branch_map):
        if self._is_root(branch):
            return branch
        if self._is_root(base_ref):
            return base_ref
        owners = self.root_owners_for_branch(branch)
        return owners[0] if len(owners) == 1 else None

    def _root_for_base(self, base_ref, branch_map):
        if not base_ref:
            return None
        if self._is_root(base_ref):
            return base_ref
        if base_ref in branch_map:
            return self.select_root_owner(
                base_ref, branch_map[base_ref].base_ref_name, branch_map
            )
        return None

    def _collect_declared_base_edges(self, prs, branch_map):
        edges = []
        for pr in prs:
            branch, base = pr.head_ref_name, pr.base_ref_name
            if (
                self._is_root(branch)
                or not base
                or (base not in branch_map and not self._is_root(base))
            ):
                continue
            root = self.select_root_owner(branch, base, branch_map)
            base_root = self._root_for_base(base, branch_map)
            same = bool(root and base_root == root)
            if same and self.git.is_ancestor(base, branch):
                edges.append(
                    self._edge(
                        base,
                        branch,
                        "declared_pr_base",
                        "executable",
                        "executable",
                        "high",
                        [
                            f"base_ref_name={base}",
                            f"{base} is ancestor of {branch}",
                            "same root family",
                        ],
                        root,
                    )
                )
            elif same:
                edges.append(
                    self._edge(
                        base,
                        branch,
                        "declared_base_mismatch",
                        "executable",
                        "needs_restack",
                        "medium",
                        [
                            f"base_ref_name={base}",
                            f"{base} is not ancestor of {branch}",
                            "same root family",
                        ],
                        root,
                    )
                )
            else:
                edges.append(
                    self._edge(
                        base,
                        branch,
                        "declared_base_mismatch",
                        "triage_only",
                        "triage_only",
                        "medium",
                        [
                            f"base_ref_name={base}",
                            "declared base is not in same root family",
                        ],
                        root,
                    )
                )
        return edges

    def _collect_nearest_same_root_edges(self, prs, branch_map, existing_edges):
        edges = []
        branches = [
            pr.head_ref_name for pr in prs if not self._is_root(pr.head_ref_name)
        ]
        existing_exec_to = {
            e.to_ref for e in existing_edges if e.classification == "executable"
        }
        for pr in prs:
            branch = pr.head_ref_name
            if self._is_root(branch) or branch in existing_exec_to:
                continue
            root = self.select_root_owner(branch, pr.base_ref_name, branch_map)
            if not root:
                continue
            candidates = []
            for cand in branches:
                if cand == branch:
                    continue
                cand_root = self.select_root_owner(
                    cand, branch_map[cand].base_ref_name, branch_map
                )
                if cand_root == root and self.git.is_ancestor(cand, branch):
                    candidates.append(
                        (self.git.commit_distance(cand, branch) or 10**9, cand)
                    )
            if candidates:
                candidates.sort()
                nearest = candidates[0][1]
                edges.append(
                    self._edge(
                        nearest,
                        branch,
                        "nearest_same_root_ancestor",
                        "executable",
                        "needs_restack",
                        "medium",
                        [
                            f"nearest same-root ancestor={nearest}",
                            "declared PR base was not executable",
                        ],
                        root,
                    )
                )
        return edges

    def _collect_cross_root_edges(self, prs):
        edges = []
        for pr in prs:
            if self._is_root(pr.head_ref_name):
                continue
            owners = self.root_owners_for_branch(pr.head_ref_name)
            if len(owners) > 1:
                for owner in owners:
                    edges.append(
                        self._edge(
                            owner,
                            pr.head_ref_name,
                            "cross_root_ancestry",
                            "blocked",
                            "blocked",
                            "high",
                            [
                                f"{owner} is ancestor of {pr.head_ref_name}",
                                "branch has multiple configured root owners",
                            ],
                            None,
                        )
                    )
        return edges

    def _collect_merge_edges(self, prs, branch_map):
        edges = []
        for pr in prs:
            branch = pr.head_ref_name
            if self._is_root(branch):
                continue
            root = self.select_root_owner(branch, pr.base_ref_name, branch_map)
            if not root:
                continue
            for line in self.git.merge_commits_between(root, branch):
                parts = line.split("")
                if len(parts) < 3:
                    continue
                sha, parents, subject = parts[0], parts[1].split(), parts[2]
                for psha in parents[1:]:
                    known = next(
                        (
                            name
                            for name, pri in branch_map.items()
                            if pri.head_ref_oid == psha
                        ),
                        None,
                    )
                    if known:
                        edges.append(
                            self._edge(
                                known,
                                branch,
                                "known_pr_merge",
                                "triage_only",
                                "triage_only",
                                "medium",
                                [
                                    f"merge_commit={sha}",
                                    f"subject={subject}",
                                    f"merged known PR branch={known}",
                                ],
                                root,
                            )
                        )
                    elif self.git.is_ancestor(psha, root):
                        edges.append(
                            self._edge(
                                root,
                                branch,
                                "trunk_update_merge",
                                "blocked",
                                "blocked",
                                "high",
                                [
                                    f"merge_commit={sha}",
                                    f"subject={subject}",
                                    f"merged trunk/root branch={root}",
                                ],
                                root,
                            )
                        )
                    else:
                        edges.append(
                            self._edge(
                                psha,
                                branch,
                                "foreign_dag_merge",
                                "blocked",
                                "blocked",
                                "high",
                                [
                                    f"merge_commit={sha}",
                                    f"subject={subject}",
                                    f"foreign parent sha={psha}",
                                ],
                                root,
                            )
                        )
        return edges

    def _collect_patch_overlap_edges(self, prs, branch_map):
        edges = []
        branches = [
            pr.head_ref_name for pr in prs if not self._is_root(pr.head_ref_name)
        ]
        for i, a in enumerate(branches):
            root_a = self.select_root_owner(a, branch_map[a].base_ref_name, branch_map)
            if not root_a:
                continue
            for b in branches[i + 1 :]:
                root_b = self.select_root_owner(
                    b, branch_map[b].base_ref_name, branch_map
                )
                if root_a != root_b:
                    continue
                overlap = self.git.patch_ids_between(
                    root_a, a
                ) & self.git.patch_ids_between(root_a, b)
                if overlap:
                    edges.append(
                        self._edge(
                            a,
                            b,
                            "patch_id_overlap",
                            "triage_only",
                            "triage_only",
                            "medium",
                            [
                                f"shared patch-id count={len(overlap)}",
                                "patch equivalence is not sufficient for Graphite parentage",
                            ],
                            root_a,
                        )
                    )
        return edges
