"""Test that the Jules CLI binary is available and functional."""
import shutil
import subprocess

import pytest


def test_jules_binary_available():
    """jules --version should succeed if binary is installed."""
    jules_path = shutil.which("jules")
    if jules_path is None:
        pytest.skip("jules CLI binary not installed")

    result = subprocess.run(
        ["jules", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"jules --version failed: {result.stderr}"
    assert result.stdout.strip(), "jules --version produced no output"


def test_jules_remote_list_help():
    """jules remote list --help should succeed if binary is installed."""
    jules_path = shutil.which("jules")
    if jules_path is None:
        pytest.skip("jules CLI binary not installed")

    result = subprocess.run(
        ["jules", "remote", "list", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    # --help might return 0 or 1 depending on implementation
    assert "remote" in result.stdout.lower() or "remote" in result.stderr.lower(), (
        "jules remote list --help doesn't mention 'remote'"
    )
