"""Validate that all Python tools import from the new structure."""
import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
TOOLS_DIR = REPO_ROOT / "tools"


def test_api_client_imports():
    """tools/api/jules_api_client.py imports successfully."""
    from tools.api.jules_api_client import JulesAPIClient
    assert JulesAPIClient is not None


def test_sessions_config_imports():
    """tools/sessions/config.py imports successfully."""
    from tools.sessions.config import calculate_grade
    assert callable(calculate_grade)


def test_sessions_list_sessions_imports():
    """tools/sessions/jules_list_sessions.py imports successfully."""
    from tools.sessions.jules_list_sessions import main
    assert callable(main)


def test_sessions_list_activities_imports():
    """tools/sessions/jules_list_activities.py imports successfully."""
    from tools.sessions.jules_list_activities import main
    assert callable(main)


def test_sessions_send_message_imports():
    """tools/sessions/jules_send_message.py imports successfully."""
    from tools.sessions.jules_send_message import send_message
    assert callable(send_message)


def test_sessions_approve_plan_imports():
    """tools/sessions/jules_approve_plan.py imports successfully."""
    from tools.sessions.jules_approve_plan import approve_plan
    assert callable(approve_plan)


def test_pr_context_imports():
    """tools/pr/jules_pr_context.py imports successfully."""
    from tools.pr.jules_pr_context import main
    assert callable(main)


def test_pr_triage_imports():
    """tools/pr/jules_pr_triage.py imports successfully."""
    from tools.pr.jules_pr_triage import main
    assert callable(main)


def test_rebase_orchestrator_imports():
    """tools/rebase/jules_rebase_orchestrator.py imports successfully."""
    from tools.rebase.jules_rebase_orchestrator import main
    assert callable(main)


def test_multi_repo_imports():
    """tools/multi_repo/jules_multi_repo.py imports successfully."""
    from tools.multi_repo.jules_multi_repo import main
    assert callable(main)


def test_utils_auth_manager_imports():
    """tools/utils/auth_manager.py imports successfully."""
    from tools.utils.auth_manager import get_jules_key, get_github_token, AuthError
    assert callable(get_jules_key)
    assert callable(get_github_token)
    assert issubclass(AuthError, Exception)


def test_cli_manager_imports():
    """tools/cli/jules-manager.py imports successfully."""
    # jules-manager.py has a hyphen, so we need importlib
    cli_path = TOOLS_DIR / "cli" / "jules-manager.py"
    assert cli_path.exists(), f"CLI manager not found at {cli_path}"

    # Can't directly import due to hyphen in filename, but we can verify it's valid Python
    import ast
    content = cli_path.read_text()
    ast.parse(content)  # Raises SyntaxError if invalid
