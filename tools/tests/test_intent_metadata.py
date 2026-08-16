"""Offline unit tests for tools/sessions/jules_intent_metadata.py.

Pure/offline: no API access, no JULES_API_KEY required.
"""
import pytest

from tools.sessions import jules_intent_metadata as jm


class _Args:
    """Minimal argparse-like namespace for filter_sessions."""

    state = None
    exclude_state = None
    pending = False
    active_only = False
    repo = None
    created_after = None
    created_before = None
    updated_after = None
    updated_before = None


@pytest.mark.offline
def test_extract_repo_from_source():
    s = {"sourceContext": {"source": "sources/github/MasumRab/EmailIntelligence"}}
    assert jm.extract_repo(s) == "MasumRab/EmailIntelligence"


@pytest.mark.offline
def test_extract_repo_from_pr_url():
    s = {
        "outputs": [
            {"pullRequest": {"url": "https://github.com/MasumRab/EmailIntelligence/pull/792"}}
        ]
    }
    assert jm.extract_repo(s) == "MasumRab/EmailIntelligence"


@pytest.mark.offline
def test_extract_repo_none():
    assert jm.extract_repo({}) is None


@pytest.mark.offline
def test_extract_pr_refs_dedupes():
    s = {
        "outputs": [
            {"pullRequest": {"url": "https://github.com/MasumRab/EmailIntelligence/pull/792"}},
            {"pullRequest": {"url": "https://github.com/MasumRab/EmailIntelligence/pull/792"}},
            {"pullRequest": {"url": "https://github.com/MasumRab/EmailIntelligence/pull/800"}},
        ]
    }
    assert jm.extract_pr_refs(s) == ["EmailIntelligence#792", "EmailIntelligence#800"]


@pytest.mark.offline
def test_extract_pr_refs_handles_flattened_pr_urls():
    s = {"pr_urls": ["https://github.com/MasumRab/jules/pull/12"]}
    assert jm.extract_pr_refs(s) == ["jules#12"]


@pytest.mark.offline
def test_extract_pr_refs_empty():
    assert jm.extract_pr_refs({}) == []


@pytest.mark.offline
def test_distill_intent_strips_persona():
    prompt = (
        'You are "Bolt", a senior engineer.\n'
        'name = "audit-task"\n'
        'description = "Audit the cache.\n'
        'schedule = "0 3 * * *"\n'
        'prompt = """\n'
        "Review the authentication flow for command injection\n"
        "and fix any vulnerabilities found.\n"
        '"""\n'
    )
    session = {"prompt": prompt, "title": "Task"}
    intent = jm.distill_intent(session)
    assert "authentication flow" in intent
    assert "Bolt" not in intent
    assert "audit-task" not in intent
    assert "0 3 * * *" not in intent


@pytest.mark.offline
def test_distill_intent_falls_back_to_title():
    session = {"prompt": "", "title": "Fix the flaky scheduler"}
    assert jm.distill_intent(session) == "Fix the flaky scheduler"


@pytest.mark.offline
def test_distill_intent_truncates():
    session = {"prompt": "word " * 100, "title": "T"}
    intent = jm.distill_intent(session, max_chars=50)
    assert len(intent) <= 50


@pytest.mark.offline
def test_build_intent_metadata_keys():
    s = {
        "id": "sessions/123",
        "name": "sessions/123",
        "state": "AWAITING_USER_FEEDBACK",
        "title": "Do the thing",
        "createTime": "2026-08-16T01:00:00Z",
        "updateTime": "2026-08-17T01:00:00Z",
        "prompt": "Implement feature X.",
        "sourceContext": {
            "source": "sources/github/MasumRab/EmailIntelligence",
            "githubRepoContext": {"startingBranch": "jules/fix"},
        },
        "outputs": [
            {"pullRequest": {"url": "https://github.com/MasumRab/EmailIntelligence/pull/1"}}
        ],
    }
    meta = jm.build_intent_metadata(s)
    assert set(meta) == {
        "id", "state", "title", "createTime", "updateTime",
        "repo", "startingBranch", "pr_refs", "intent", "prompt_tail",
    }
    assert meta["id"] == "123"
    assert meta["startingBranch"] == "jules/fix"
    assert meta["repo"] == "MasumRab/EmailIntelligence"
    assert meta["pr_refs"] == ["EmailIntelligence#1"]
    assert meta["prompt_tail"] == "Implement feature X."
    assert meta["intent"] == "Implement feature X."


@pytest.mark.offline
def test_filter_sessions_by_state_and_repo():
    sessions = [
        {
            "id": "1", "state": "AWAITING_USER_FEEDBACK",
            "sourceContext": {"source": "sources/github/MasumRab/EmailIntelligence"},
            "createTime": "2026-08-01T00:00:00Z",
        },
        {
            "id": "2", "state": "COMPLETED",
            "sourceContext": {"source": "sources/github/MasumRab/jules"},
            "createTime": "2026-08-02T00:00:00Z",
        },
        {
            "id": "3", "state": "FAILED",
            "sourceContext": {"source": "sources/github/MasumRab/EmailIntelligence"},
            "createTime": "2026-08-03T00:00:00Z",
        },
    ]
    args = _Args()
    args.state = ["AWAITING_USER_FEEDBACK", "FAILED"]
    args.repo = "emailintelligence"
    out = jm.filter_sessions(sessions, args)
    assert [s["id"] for s in out] == ["1", "3"]


@pytest.mark.offline
def test_filter_sessions_by_date_window():
    sessions = [
        {"id": "1", "state": "IN_PROGRESS", "createTime": "2026-08-01T00:00:00Z",
         "updateTime": "2026-08-02T00:00:00Z"},
        {"id": "2", "state": "IN_PROGRESS", "createTime": "2026-08-10T00:00:00Z",
         "updateTime": "2026-08-15T00:00:00Z"},
        {"id": "3", "state": "IN_PROGRESS", "createTime": "2026-08-20T00:00:00Z",
         "updateTime": "2026-08-25T00:00:00Z"},
        {"id": "4", "state": "IN_PROGRESS", "createTime": None, "updateTime": None},
    ]
    args = _Args()
    args.created_after = "2026-08-05"
    args.created_before = "2026-08-15"
    args.updated_before = "2026-08-16"
    out = jm.filter_sessions(sessions, args)
    assert [s["id"] for s in out] == ["2"]


@pytest.mark.offline
def test_filter_sessions_pending_and_active_only():
    sessions = [
        {"id": "1", "state": "COMPLETED", "createTime": "2026-08-01T00:00:00Z"},
        {"id": "2", "state": "QUEUED", "createTime": "2026-08-01T00:00:00Z"},
        {"id": "3", "state": "FAILED", "createTime": "2026-08-01T00:00:00Z"},
    ]
    args = _Args()
    args.pending = True
    assert [s["id"] for s in jm.filter_sessions(sessions, args)] == ["3"]

    args2 = _Args()
    args2.active_only = True
    assert [s["id"] for s in jm.filter_sessions(sessions, args2)] == ["2", "3"]
