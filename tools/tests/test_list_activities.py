"""Offline unit tests for tools/sessions/jules_list_activities.py.

Pure/offline: no API access, no JULES_API_KEY required.
"""
import pytest

from tools.sessions import jules_list_activities as ja


AGENT_LONG = "x" * 300
USER_LONG = "y" * 300


@pytest.mark.offline
def test_format_activity_agent_message_truncates_by_default():
    act = {
        "originator": "agent",
        "createTime": "2026-08-16T17:25:02Z",
        "agentMessaged": {"agentMessage": AGENT_LONG},
    }
    assert ja.format_activity(act) == (
        "[2026-08-16T17:25:02Z] agent: Agent Messaged - "
        f"{'x' * 100}..."
    )


@pytest.mark.offline
def test_format_activity_agent_message_full():
    act = {
        "originator": "agent",
        "createTime": "2026-08-16T17:25:02Z",
        "agentMessaged": {"agentMessage": AGENT_LONG},
    }
    assert ja.format_activity(act, full=True) == (
        "[2026-08-16T17:25:02Z] agent: Agent Messaged - "
        f"{AGENT_LONG}"
    )


@pytest.mark.offline
def test_format_activity_user_message_truncates_by_default():
    act = {
        "originator": "user",
        "createTime": "2026-08-16T18:00:00Z",
        "userMessaged": {"userMessage": USER_LONG},
    }
    assert ja.format_activity(act) == (
        "[2026-08-16T18:00:00Z] user: User Messaged - "
        f"{'y' * 100}..."
    )


@pytest.mark.offline
def test_format_activity_user_message_full():
    act = {
        "originator": "user",
        "createTime": "2026-08-16T18:00:00Z",
        "userMessaged": {"userMessage": USER_LONG},
    }
    assert ja.format_activity(act, full=True) == (
        "[2026-08-16T18:00:00Z] user: User Messaged - "
        f"{USER_LONG}"
    )


@pytest.mark.offline
def test_format_activity_short_message_keeps_default_ellipsis():
    act = {
        "originator": "agent",
        "createTime": "2026-08-16T17:25:02Z",
        "agentMessaged": {"agentMessage": "short"},
    }
    assert ja.format_activity(act) == (
        "[2026-08-16T17:25:02Z] agent: Agent Messaged - short..."
    )


@pytest.mark.offline
def test_format_activity_short_message_full_has_no_ellipsis():
    act = {
        "originator": "agent",
        "createTime": "2026-08-16T17:25:02Z",
        "agentMessaged": {"agentMessage": "short"},
    }
    assert ja.format_activity(act, full=True) == (
        "[2026-08-16T17:25:02Z] agent: Agent Messaged - short"
    )


@pytest.mark.offline
def test_format_activity_other_event_types_unaffected():
    plan = {
        "originator": "system",
        "createTime": "2026-08-16T10:00:00Z",
        "planGenerated": {"plan": {"steps": [{"title": "Step one"}]}},
    }
    assert ja.format_activity(plan, full=True) == (
        "[2026-08-16T10:00:00Z] system: Plan Generated\n  - Step one"
    )