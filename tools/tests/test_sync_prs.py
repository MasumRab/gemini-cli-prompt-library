"""Offline regression tests for explicit PR-store sync semantics."""

from tools.store import sync_prs


class FakeStore:
    def __init__(self):
        self.upserted = []
        self.watermarks = []

    def upsert_prs(self, repo, prs):
        self.upserted.append((repo, prs))
        return len(prs)

    def set_watermark(self, key):
        self.watermarks.append(key)


def test_sync_repo_always_fetches_when_explicit_even_if_fresh(monkeypatch):
    """An explicit request must not consult age or skip the API fetch."""
    store = FakeStore()
    requests = []

    def fake_gh_list(repo, state, limit, fields=sync_prs.PR_FIELDS):
        requests.append((repo, state, limit))
        return [{"number": len(requests), "state": state.upper()}]

    monkeypatch.setattr(sync_prs, "gh_pr_list", fake_gh_list)
    monkeypatch.setattr(sync_prs, "fetch_rollups", lambda repo, prs: None)

    result = sync_prs.sync_repo(store, "EmailIntelligence")

    assert result.startswith("synced 3 PRs")
    assert [state for _, state, _ in requests] == ["open", "merged", "closed"]
    assert len(store.upserted) == 1
    assert store.watermarks == ["last_pr_sync:EmailIntelligence"]


def test_status_mode_reports_age_without_sync(monkeypatch, capsys):
    """Status mode reads freshness metadata and exits before sync_repo."""
    class StatusStore:
        def get_watermark(self, key):
            return "2026-09-26T00:00:00Z"

        def _conn(self):
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            conn.execute("CREATE TABLE pull_request (repo TEXT, state TEXT)")
            return _Context(conn)

        def is_repo_stale(self, repo, max_age):
            return True

    class _Context:
        def __init__(self, conn):
            self.conn = conn

        def __enter__(self):
            return self.conn

        def __exit__(self, *exc):
            self.conn.close()

    monkeypatch.setattr(sync_prs, "PRStore", StatusStore)
    monkeypatch.setattr(
        sync_prs,
        "sync_repo",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("--status must not sync")
        ),
    )
    monkeypatch.setattr("sys.argv", ["sync_prs.py", "--repo", "EmailIntelligence", "--status"])

    assert sync_prs.main() == 0
    assert "stale=True" in capsys.readouterr().out
