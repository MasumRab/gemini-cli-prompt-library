"""Shared test fixtures for Jules tools test suite."""
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"

OFFICIAL_STATES = [
    "QUEUED",
    "PLANNING",
    "AWAITING_PLAN_APPROVAL",
    "AWAITING_USER_FEEDBACK",
    "IN_PROGRESS",
    "PAUSED",
    "COMPLETED",
    "FAILED",
    "STATE_UNSPECIFIED",
]

INVALID_STATES = ["RUNNING", "PENDING", "WAITING_FOR_USER", "RUNNING_STUCK"]


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def mock_session_completed():
    return {
        "name": "sessions/test-session-001",
        "state": "COMPLETED",
        "title": "Fix authentication bug",
        "repository": "MasumRab/jules",
        "headBranch": "jules/fix-auth-bug",
        "pullRequest": {"url": "https://github.com/MasumRab/jules/pull/1"},
    }


@pytest.fixture
def mock_session_awaiting_approval():
    return {
        "name": "sessions/test-session-002",
        "state": "AWAITING_PLAN_APPROVAL",
        "title": "Add new feature",
        "repository": "MasumRab/jules",
        "headBranch": "jules/add-feature",
    }


@pytest.fixture
def mock_session_awaiting_feedback():
    return {
        "name": "sessions/test-session-003",
        "state": "AWAITING_USER_FEEDBACK",
        "title": "Refactor database layer",
        "repository": "MasumRab/jules",
        "headBranch": "jules/refactor-db",
    }


@pytest.fixture
def mock_session_failed():
    return {
        "name": "sessions/test-session-004",
        "state": "FAILED",
        "title": "Fix CI pipeline",
        "repository": "MasumRab/jules",
        "headBranch": "jules/fix-ci",
        "error": "Build failed: missing dependency",
    }


@pytest.fixture
def mock_session_in_progress():
    return {
        "name": "sessions/test-session-005",
        "state": "IN_PROGRESS",
        "title": "Update documentation",
        "repository": "MasumRab/jules",
        "headBranch": "jules/update-docs",
    }


@pytest.fixture
def mock_activities():
    return [
        {"type": "agentMessaged", "timestamp": "2026-07-01T10:00:00Z", "content": "Starting work"},
        {"type": "userMessaged", "timestamp": "2026-07-01T10:05:00Z", "content": "Please focus on auth"},
        {"type": "progressUpdated", "timestamp": "2026-07-01T10:10:00Z", "content": "50% complete"},
        {"type": "planApproved", "timestamp": "2026-07-01T10:15:00Z"},
    ]


@pytest.fixture
def mock_api_client():
    """Mock JulesAPIClient that returns canned responses."""
    client = MagicMock()
    client.list_sessions.return_value = [
        {"name": "sessions/test-001", "state": "COMPLETED"},
        {"name": "sessions/test-002", "state": "AWAITING_USER_FEEDBACK"},
    ]
    client.send_message.return_value = {"result": "ok"}
    client.approve_plan.return_value = {"result": "ok"}
    return client


@pytest.fixture
def repo_root():
    """Path to the jules repo root."""
    return Path(__file__).parent.parent.parent
