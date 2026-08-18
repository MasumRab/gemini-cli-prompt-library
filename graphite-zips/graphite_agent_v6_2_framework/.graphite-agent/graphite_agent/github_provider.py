import json

from .models import PullRequestInfo


class GitHubPullRequestProvider:
    def __init__(self, git):
        self.git = git

    def _escape(self, value):
        # JSON string escaping without surrounding quotes.
        return json.dumps(str(value))[1:-1]

    def repo_metadata(self):
        raw = self.git.run(["gh", "repo", "view", "--json", "owner,name"], check=False)
        if not raw:
            raise RuntimeError("Could not read GitHub repository metadata via gh.")
        data = json.loads(raw)
        return {"owner": data["owner"]["login"], "name": data["name"]}

    def list_open_prs(self):
        repo = self.repo_metadata()
        owner = self._escape(repo["owner"])
        name = self._escape(repo["name"])
        prs = []
        has_next_page = True
        after = "null"
        while has_next_page:
            query = f"""
            query {{
              repository(owner: "{owner}", name: "{name}") {{
                pullRequests(states: OPEN, first: 100, after: {after}) {{
                  pageInfo {{ hasNextPage endCursor }}
                  nodes {{
                    number title url state isDraft headRefName headRefOid baseRefName
                    reviewDecision mergeStateStatus mergeable
                    commits(last: 1) {{ nodes {{ commit {{ oid }} }} }}
                  }}
                }}
              }}
            }}
            """
            raw = self.git.run(
                ["gh", "api", "graphql", "-f", f"query={query}"], check=False
            )
            if not raw:
                raise RuntimeError("Could not fetch open PRs via GitHub GraphQL.")
            pr_data = (
                json.loads(raw)
                .get("data", {})
                .get("repository", {})
                .get("pullRequests", {})
            )
            for pr in pr_data.get("nodes", []):
                prs.append(
                    PullRequestInfo(
                        number=pr.get("number"),
                        title=pr.get("title"),
                        url=pr.get("url"),
                        head_ref_name=pr["headRefName"],
                        head_ref_oid=pr.get("headRefOid"),
                        base_ref_name=pr.get("baseRefName"),
                        is_draft=pr.get("isDraft", False),
                        review_decision=pr.get("reviewDecision"),
                        merge_state_status=pr.get("mergeStateStatus"),
                        mergeable=pr.get("mergeable"),
                        raw=pr,
                    )
                )
            info = pr_data.get("pageInfo", {})
            has_next_page = info.get("hasNextPage", False)
            if has_next_page:
                after = f'"{info.get("endCursor")}"'
        return prs
