import json
from .schemas import PR


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
                        number=p.get("number"),
                        title=p.get("title"),
                        url=p.get("url"),
                        head_ref_name=p["headRefName"],
                        head_ref_oid=p.get("headRefOid"),
                        base_ref_name=p.get("baseRefName"),
                        is_draft=p.get("isDraft", False),
                        review_decision=p.get("reviewDecision"),
                        merge_state_status=p.get("mergeStateStatus"),
                        mergeable=p.get("mergeable"),
                        raw=p,
                    )
                )
            pi = pd.get("pageInfo", {})
            more = pi.get("hasNextPage", False)
            after = '"%s"' % pi.get("endCursor") if more else after
        return prs
