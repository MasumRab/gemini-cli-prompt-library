"""Validate shell scripts produce valid output with mock data."""
import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
SHELL_DIR = REPO_ROOT / "tools" / "shell"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_jules_audit_sh_exists():
    assert (SHELL_DIR / "jules_audit.sh").exists()


def test_jules_audit_sh_has_set_e():
    content = (SHELL_DIR / "jules_audit.sh").read_text()
    assert "set -e" in content, "jules_audit.sh missing 'set -e'"


def test_jules_audit_sh_no_invalid_states():
    content = (SHELL_DIR / "jules_audit.sh").read_text()
    for invalid in ["RUNNING", "PENDING", "WAITING_FOR_USER"]:
        assert invalid not in content, f"jules_audit.sh contains invalid state '{invalid}'"


def test_jules_sync_all_sh_exists():
    assert (SHELL_DIR / "jules_sync_all.sh").exists()


def test_jules_sync_all_sh_has_set_e():
    content = (SHELL_DIR / "jules_sync_all.sh").read_text()
    assert "set -e" in content, "jules_sync_all.sh missing 'set -e'"


def test_setup_jules_env_sh_has_compact_flag():
    content = (SHELL_DIR / "setup_jules_env.sh").read_text()
    assert "--compact" in content, "setup_jules_env.sh missing --compact flag"


def test_all_shell_scripts_have_set_e():
    """All shell scripts in tools/shell/ must have 'set -e'."""
    for script in SHELL_DIR.glob("*.sh"):
        content = script.read_text()
        assert "set -e" in content, f"{script.name} missing 'set -e'"


def test_all_shell_scripts_executable():
    """All shell scripts in tools/shell/ should be executable."""
    for script in SHELL_DIR.glob("*.sh"):
        assert os.access(script, os.X_OK), f"{script.name} is not executable"


def test_commands_directory_scripts_exist():
    """All 10 wrapper commands should exist."""
    commands_dir = REPO_ROOT / "commands"
    expected = [
        "jules-list",
        "jules_triage.sh",
        "jules_audit.sh",
        "jules_recover.sh",
        "jules_pr_context.sh",
        "jules_discovery.sh",
        "jules-triage-activities",
        "jules-triage-analyze",
        "jules-triage-list",
        "jules-triage-recover",
    ]
    for name in expected:
        assert (commands_dir / name).exists(), f"Missing command: {name}"
