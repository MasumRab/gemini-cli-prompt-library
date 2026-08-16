"""Offline unit tests for tools/sessions/jules_intent_metadata.py.

Pure/offline: no API access, no JULES_API_KEY required.
"""
import pytest

from tools.sessions import jules_intent_metadata as jm
from tools.sessions import config as cfg


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


# ---------------------------------------------------------------------------
# distill_intent_rich heuristics
# ---------------------------------------------------------------------------


@pytest.mark.offline
def test_distill_intent_rich_code_review_request_title():
    prompt = (
        "## Code Review Request\n\n"
        "Title: Fix the flaky scheduler\n\n"
        "Please review the changes on this branch.\n"
    )
    intent = jm.distill_intent_rich({"prompt": prompt, "title": "something"})
    assert intent.startswith("review PR: ")
    assert "Fix the flaky scheduler" in intent


@pytest.mark.offline
def test_distill_intent_rich_strips_persona_blocks():
    prompt = (
        'You are "Bolt", a senior engineer.\n'
        'name = "audit-task"\n'
        'description = "Audit the cache.\n'
        'schedule = "0 3 * * *"\n'
        "Review the authentication flow for command injection\n"
    )
    intent = jm.distill_intent_rich({"prompt": prompt, "title": "Task"})
    assert "authentication flow" in intent
    assert "Bolt" not in intent
    assert "audit-task" not in intent


@pytest.mark.offline
def test_distill_intent_rich_mission_tail_extraction():
    prompt = (
        'You are "Turbo", a performance-obsessed engineer.\n'
        "Your mission is to reduce the cold-start latency of the cache server.\n"
    )
    intent = jm.distill_intent_rich({"prompt": prompt, "title": "Task"})
    assert "cold-start latency" in intent


@pytest.mark.offline
def test_distill_intent_rich_priority_pr_task():
    prompt = (
        "PRIORITY PR TASK: fix failing CI on EmailIntelligence\n"
        "goal: stabilize the build pipeline\n"
        "title: Fix flaky unit tests\n"
        "PR REPAIR: #792\n"
    )
    intent = jm.distill_intent_rich({"prompt": prompt, "title": "x"})
    assert "stabilize the build pipeline" in intent
    assert "PR #792" in intent


@pytest.mark.offline
def test_distill_intent_rich_description_block_capture():
    prompt = (
        "description: >\n"
        "  Refactor the scheduler so it never drops tasks\n"
        "  under load.\n"
    )
    intent = jm.distill_intent_rich({"prompt": prompt, "title": "x"})
    assert "Refactor the scheduler" in intent


@pytest.mark.offline
def test_distill_intent_rich_goal_line_capture():
    prompt = "objective: unblock the release train by fixing the auth regression"
    intent = jm.distill_intent_rich({"prompt": prompt, "title": "x"})
    assert "release train" in intent


@pytest.mark.offline
def test_distill_intent_rich_generic_template_rejection():
    prompt = "Read the issue description completely and then select the target PR."
    intent = jm.distill_intent_rich({"prompt": prompt, "title": "Fix the cache eviction bug"})
    assert "Read the issue description" not in intent
    assert intent == "Fix the cache eviction bug"


@pytest.mark.offline
def test_distill_intent_wrapper_uses_rich_then_simple():
    prompt = (
        "## Code Review Request\n\n"
        "Title: Audit the release pipeline\n\n"
        "Please review the diff."
    )
    intent = jm.distill_intent({"prompt": prompt, "title": "T"})
    assert intent.startswith("review PR: ")


# ---------------------------------------------------------------------------
# classify_session
# ---------------------------------------------------------------------------


@pytest.mark.offline
def test_classify_has_pr():
    s = {
        "state": "COMPLETED",
        "title": "Implement the export feature",
        "outputs": [{"pullRequest": {"url": "https://github.com/MasumRab/EmailIntelligence/pull/9"}}],
    }
    assert jm.classify_session(s)["bucket"] == "has_pr"


@pytest.mark.offline
def test_classify_code_review_type():
    s = {"state": "COMPLETED", "title": "Fix failing CI on main"}
    assert jm.classify_session(s)["bucket"] == "code_review_type"


@pytest.mark.offline
def test_classify_execution_type():
    s = {"state": "COMPLETED", "title": "Implement the export feature"}
    assert jm.classify_session(s)["bucket"] == "execution_type"


@pytest.mark.offline
def test_classify_other():
    s = {"state": "IN_PROGRESS", "title": "Implement the export feature"}
    assert jm.classify_session(s)["bucket"] == "other"


# ---------------------------------------------------------------------------
# is_stale / db_anomalies
# ---------------------------------------------------------------------------


@pytest.mark.offline
def test_is_stale():
    assert jm.is_stale({"updateTime": "2026-08-01T10:00:00Z"}, "2026-08-15")
    assert not jm.is_stale({"updateTime": "2026-08-16T10:00:00Z"}, "2026-08-15")
    assert not jm.is_stale({}, "2026-08-15")


@pytest.mark.offline
def test_db_anomalies():
    sessions = [
        {"id": "1", "state": "IN_PROGRESS", "createTime": "2026-08-01T00:00:00Z", "updateTime": None},
        {"id": "2", "state": "COMPLETED", "createTime": "2026-08-02T00:00:00Z",
         "updateTime": "2026-08-01T00:00:00Z"},
        {"id": "3", "state": "AWAITING_USER_FEEDBACK", "createTime": "2025-11-01T00:00:00Z",
         "updateTime": "2025-11-02T00:00:00Z"},
        {"id": "4", "state": "FAILED", "createTime": "2025-06-01T00:00:00Z",
         "updateTime": "2025-06-02T00:00:00Z"},
    ]
    reasons = dict(jm.db_anomalies(sessions))
    assert reasons["1"] == "missing updateTime"
    assert "updateTime < createTime" in reasons["2"]
    assert "non-terminal with createTime in 2025" in reasons["3"]
    assert "4" not in reasons


# ---------------------------------------------------------------------------
# tools/sessions/config.py shared state constants
# ---------------------------------------------------------------------------


@pytest.mark.offline
def test_config_no_action_states():
    assert cfg.NO_ACTION_STATES == frozenset(
        {"COMPLETED", "QUEUED", "PLANNING", "STATE_UNSPECIFIED"}
    )


@pytest.mark.offline
def test_config_likely_pending():
    assert not cfg.likely_pending("COMPLETED")
    assert not cfg.likely_pending("queued")
    assert not cfg.likely_pending("planning")
    assert cfg.likely_pending("FAILED")
    assert cfg.likely_pending("AWAITING_USER_FEEDBACK")
    assert cfg.likely_pending("SOME_FUTURE_STATE")


@pytest.mark.offline
def test_config_normalize_state():
    assert cfg.normalize_state("in_progress") == "IN_PROGRESS"
    assert cfg.normalize_state("COMPLETED") == "COMPLETED"
    assert cfg.normalize_state(None) == "UNKNOWN"
    assert cfg.normalize_state("") == "UNKNOWN"


# ---------------------------------------------------------------------------
# refactored consumers still import/run offline
# ---------------------------------------------------------------------------


@pytest.mark.offline
def test_jules_list_sessions_imports_offline():
    from tools.sessions import jules_list_sessions

    assert jules_list_sessions.likely_pending("COMPLETED") is False
    assert jules_list_sessions.likely_pending("FAILED") is True
    assert "NO_ACTION_STATES" in dir(jules_list_sessions)
