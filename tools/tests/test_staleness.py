"""Offline tests for informational freshness and explicitly requested sync."""

from datetime import datetime, timedelta, timezone

import pytest

from tools.sessions import session_tracker
from tools.store import staleness
from tools.store.jules_store import JulesSessionStore


NOW = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def store(tmp_path):
    """Create an isolated SQLite session store."""
    return JulesSessionStore(tmp_path / "store.db")


def test_missing_marker_is_unknown_and_read_only(store, monkeypatch):
    """Missing freshness metadata is reported, never repaired by a fetch."""
    def unexpected_sync(*args, **kwargs):
        raise AssertionError("freshness inspection must not trigger sync")

    monkeypatch.setattr(staleness, "sync_store", unexpected_sync)
    status = staleness.inspect_freshness(store, now=NOW)

    assert status.last_sync is None
    assert status.age_seconds is None
    assert status.is_old is None
    assert status.timestamp_problem == "missing"
    assert staleness.get_last_sync(store) is None


def test_inspect_freshness_does_not_create_missing_store(tmp_path, monkeypatch):
    """Read-only status on a missing default store does not create directories."""
    missing_db = tmp_path / "absent" / "store.db"
    monkeypatch.setattr(staleness, "STORE_DB", missing_db)
    assert not missing_db.parent.exists()
    monkeypatch.setattr("sys.argv", ["staleness.py", "--check"])

    assert staleness.main() == 0
    assert not missing_db.parent.exists()


@pytest.mark.parametrize(
    ("age", "expected_old"),
    [(timedelta(hours=11), False), (timedelta(hours=12), False),
     (timedelta(hours=13), True)],
)
def test_age_is_informational_only(store, age, expected_old):
    """Threshold comparisons report age; they perform no update or fetch."""
    staleness.record_sync(store, synced_at=NOW - age)
    before = staleness.get_last_sync(store)

    status = staleness.inspect_freshness(store, now=NOW)

    assert status.is_old is expected_old
    assert staleness.get_last_sync(store) == before


def test_malformed_and_future_markers_are_reported(store):
    with store._conn() as conn:
        conn.execute(
            "INSERT INTO sync_meta (key, value) VALUES (?, ?)",
            (staleness.META_KEY, "not-a-timestamp"),
        )
    malformed = staleness.inspect_freshness(store, now=NOW)
    assert malformed.timestamp_problem == "malformed"
    assert malformed.is_old is None

    staleness.record_sync(store, synced_at=NOW + timedelta(minutes=5))
    future = staleness.inspect_freshness(store, now=NOW)
    assert future.timestamp_problem == "future_timestamp_or_clock_skew"
    assert future.is_old is None


def test_explicit_sync_stamps_only_after_zero_return(store, monkeypatch):
    """Only a successful explicitly invoked incremental sync records a marker."""
    from tools.store import sync_incremental

    calls = []

    def successful_sync(argv):
        calls.append(argv)
        return 0

    monkeypatch.setattr(sync_incremental, "main", successful_sync)
    assert staleness.sync_store(store) is True
    assert calls == [["--max-pages", "5"]]
    assert staleness.get_last_sync(store) is not None

    prior = staleness.get_last_sync(store)
    monkeypatch.setattr(sync_incremental, "main", lambda argv: 1)
    assert staleness.sync_store(store) is False
    assert staleness.get_last_sync(store) == prior


def test_explicit_sync_catches_initialization_exception(store, monkeypatch):
    from tools.store import sync_incremental

    def failing_sync(argv):
        raise RuntimeError("missing credentials")

    monkeypatch.setattr(sync_incremental, "main", failing_sync)
    assert staleness.sync_store(store) is False
    assert staleness.get_last_sync(store) is None


def test_tracker_reads_do_not_construct_api_client_or_sync(monkeypatch):
    """List/default tracking paths read local data only, regardless of age."""
    class FakeStore:
        pass

    fake_store = FakeStore()
    monkeypatch.setattr(session_tracker, "JulesSessionStore", lambda: fake_store)
    monkeypatch.setattr(session_tracker, "get_awaiting_sessions", lambda store: [])

    def unexpected_api_client(*args, **kwargs):
        raise AssertionError("local tracker read must not construct API client")

    monkeypatch.setattr(session_tracker, "JulesAPIClient", unexpected_api_client)
    session_tracker.list_awaiting_sessions()
    session_tracker.track_sessions(sync_first=False)


def test_tracker_explicit_sync_flag_remains_opt_in(monkeypatch):
    """The explicit tracker sync path still calls the API-backed sync function."""
    class FakeStore:
        pass

    store_obj = FakeStore()
    calls = []
    monkeypatch.setattr(session_tracker, "JulesSessionStore", lambda: store_obj)
    monkeypatch.setenv("JULES_API_KEY", "test-key-value")
    monkeypatch.setattr(session_tracker, "JulesAPIClient", lambda: object())
    monkeypatch.setattr(
        session_tracker,
        "sync_from_api",
        lambda store, client, limit: calls.append((store, client, limit)) or {},
    )
    monkeypatch.setattr(session_tracker, "get_awaiting_sessions", lambda store: [])

    session_tracker.track_sessions(sync_first=True, limit=7)

    assert len(calls) == 1
    assert calls[0][0] is store_obj
    assert calls[0][2] == 7
