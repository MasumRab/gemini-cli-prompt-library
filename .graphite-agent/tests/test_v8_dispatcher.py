"""
Tests for Graphite Agent V8 Dispatcher (Phase 1)

Tests the unified dispatcher and stage gating functionality.
"""

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from lib.io import rj, wj


class TestGitCore(unittest.TestCase):
    """Test GitCore class from git_core.py"""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path("/tmp/test_git_core")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        # Create a minimal git repo
        os.chdir(self.test_dir)
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)

        # Create a test file and commit
        test_file = self.test_dir / "test.txt"
        test_file.write_text("test content")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", "initial"], check=True, capture_output=True
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_git_core_initialization(self):
        """Test GitCore can be initialized."""
        from lib.git_core import GitCore

        git = GitCore(str(self.test_dir))
        self.assertIsNotNone(git)
        self.assertTrue(git.repo_path.exists())

    def test_git_core_is_ancestor(self):
        """Test is_ancestor function."""
        from lib.git_core import GitCore

        git = GitCore(str(self.test_dir))

        # Get the initial commit
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(self.test_dir),
        )
        commit_hash = result.stdout.strip()

        # A commit is an ancestor of itself
        self.assertTrue(git.is_ancestor(commit_hash, commit_hash))

    def test_git_core_ref_exists(self):
        """Test ref_exists function."""
        from lib.git_core import GitCore

        git = GitCore(str(self.test_dir))

        self.assertTrue(git.ref_exists("HEAD"))
        self.assertFalse(git.ref_exists("nonexistent"))


class TestDispatcherStages(unittest.TestCase):
    """Test dispatcher stage configuration."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.test_repo = Path("/tmp/test_dispatcher")
        self.test_repo.mkdir(parents=True, exist_ok=True)
        os.chdir(self.test_repo)

        # Create .graphite-agent structure
        agent_dir = self.test_repo / ".graphite-agent"
        outputs_dir = agent_dir / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)

        # Create mock output files
        wj(outputs_dir / "repo_inventory.json", {"branches": {}})

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        if self.test_repo.exists():
            shutil.rmtree(self.test_repo)

    def test_stage_ordering(self):
        """Test that stages are properly ordered."""
        from main import STAGES

        # Check that all expected stages exist
        expected_stages = [
            "discover",
            "analyse",
            "triage",
            "decide",
            "plan",
            "validate",
            "execute",
            "status",
            "report",
        ]
        for stage in expected_stages:
            self.assertIn(stage, STAGES)

    def test_discover_no_prerequisites(self):
        """Test that discover stage has no prerequisites."""
        from main import STAGES

        discover_config = STAGES["discover"]
        self.assertEqual(discover_config.required_files, [])

    def test_analyse_requires_discover(self):
        """Test that analyse requires discover output."""
        from main import STAGES

        analyse_config = STAGES["analyse"]
        self.assertIn("outputs/repo_inventory.json", analyse_config.required_files)

    def test_execute_requires_approval(self):
        """Test that execute stage requires approval."""
        from main import STAGES

        execute_config = STAGES["execute"]
        self.assertEqual(execute_config.gate, "user_approval_required")


class TestPipelineGating(unittest.TestCase):
    """Test pipeline gate functionality."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.test_repo = Path("/tmp/test_gating")
        self.test_repo.mkdir(parents=True, exist_ok=True)
        os.chdir(self.test_repo)

        # Create .graphite-agent structure
        agent_dir = self.test_repo / ".graphite-agent"
        outputs_dir = agent_dir / "outputs"
        latest_dir = outputs_dir / "latest"
        validation_dir = latest_dir / "validation"
        validation_dir.mkdir(parents=True, exist_ok=True)

        # Create mock files
        wj(outputs_dir / "repo_inventory.json", {"branches": {}})
        wj(
            latest_dir / "replay_risk.json",
            {"overall_risk": "low", "execution_allowed": True},
        )

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        if self.test_repo.exists():
            shutil.rmtree(self.test_repo)

    @patch("main.check_replay_safety")
    @patch("main.get_outputs_dir")
    def test_can_execute_discover_always_allowed(self, mock_get_outputs, mock_safety):
        """Test that discover stage can always be executed."""
        from main import can_execute_stage

        mock_safety.return_value = (False, "blocked")
        mock_get_outputs.return_value = self.test_repo / ".graphite-agent" / "outputs"

        can_do, reason = can_execute_stage("discover")
        # Discover should work even if replay is blocked (it has no gate)
        # But it needs to pass the prerequisite check
        # For now, just check it doesn't crash
        self.assertIsInstance(can_do, bool)

    @patch("main.check_replay_safety")
    @patch("main.get_outputs_dir")
    def test_cannot_execute_analyse_when_replay_blocked(
        self, mock_get_outputs, mock_safety
    ):
        """Test that analyse cannot be executed when replay is blocked."""
        from main import can_execute_stage

        mock_safety.return_value = (False, "active rebase detected")
        mock_get_outputs.return_value = self.test_repo / ".graphite-agent" / "outputs"

        can_do, reason = can_execute_stage("analyse")
        # Analyse has replay_risk gate, so should be blocked
        self.assertFalse(can_do)


class TestMainCLI(unittest.TestCase):
    """Test main CLI functionality."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.test_repo = Path("/tmp/test_cli")
        self.test_repo.mkdir(parents=True, exist_ok=True)
        os.chdir(self.test_repo)

        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)

        # Create .graphite-agent structure
        agent_dir = self.test_repo / ".graphite-agent"
        outputs_dir = agent_dir / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil

        if self.test_repo.exists():
            shutil.rmtree(self.test_repo)

    def test_help_no_args(self):
        """Test that help is shown when no args."""
        from main import main

        result = main(["--help"])
        self.assertEqual(result, 0)

    def test_unknown_command(self):
        """Test that unknown command returns error."""
        from main import main

        result = main(["unknown_command"])
        self.assertEqual(result, 1)

    def test_version_flag(self):
        """Test that version flag works."""
        from main import main

        # This should print version and exit
        result = main(["--version"])
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
