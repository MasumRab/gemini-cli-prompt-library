"""
Simple Tests for Graphite Agent V8 Dispatcher (Phase 1)

Focused tests for dispatcher stage gating functionality.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))


class TestDispatcherConfiguration(unittest.TestCase):
    """Test dispatcher stage configuration."""

    def test_all_stages_defined(self):
        """Test that all required stages are defined."""
        from main import STAGES

        required_stages = [
            "discover",
            "analyse",
            "triage",
            "decide",
            "plan",
            "validate",
            "execute",
            "status",
            "report",
            "run",
        ]

        for stage in required_stages:
            if stage == "run":
                continue  # run is not in STAGES, it's a special case
            self.assertIn(stage, STAGES, f"Missing required stage: {stage}")

    def test_discover_stage_config(self):
        """Test discover stage configuration."""
        from main import STAGES

        discover = STAGES["discover"]
        self.assertEqual(discover.name, "discover")
        self.assertEqual(
            discover.description, "Stage 1: Discover repo and assess replay risk"
        )
        self.assertEqual(discover.required_files, [])
        self.assertIn("analyse", discover.next_stages)
        self.assertIsNone(discover.gate)

    def test_analyse_stage_config(self):
        """Test analyse stage configuration."""
        from main import STAGES

        analyse = STAGES["analyse"]
        self.assertIn("outputs/repo_inventory.json", analyse.required_files)
        self.assertEqual(analyse.gate, "replay_risk")

    def test_execute_stage_requires_approval(self):
        """Test execute stage requires approval gate."""
        from main import STAGES

        execute = STAGES["execute"]
        self.assertEqual(execute.gate, "user_approval_required")


class TestDispatcherFunctions(unittest.TestCase):
    """Test dispatcher utility functions."""

    def setUp(self):
        """Set up mock environment."""
        from unittest.mock import patch

        # Mock the outputs directory
        self.mock_outputs = Path("/tmp/mock_outputs")

        self.patcher_get_outputs = patch("main.get_outputs_dir")
        self.mock_get_outputs = self.patcher_get_outputs.start()
        self.mock_get_outputs.return_value = self.mock_outputs

        self.patcher_get_agent = patch("main.get_agent_dir")
        self.mock_get_agent = self.patcher_get_agent.start()
        self.mock_get_agent.return_value = self.mock_outputs.parent

    def tearDown(self):
        """Clean up mocks."""
        self.patcher_get_outputs.stop()
        self.patcher_get_agent.stop()

    def test_can_execute_discover_with_no_files(self):
        """Test discover can execute with no output files."""
        from main import can_execute_stage

        can_do, reason = can_execute_stage("discover")
        # Discover has no required files, should pass if outputs dir exists
        self.assertTrue(can_do or "Missing required file" not in reason)

    def test_cannot_execute_analyse_without_discover_output(self):
        """Test analyse cannot execute without discover output."""
        from main import can_execute_stage

        can_do, reason = can_execute_stage("analyse")
        # Analyse requires repo_inventory.json which doesn't exist
        self.assertFalse(can_do)
        self.assertIn("Missing required file", reason)

    def test_execute_blocked_by_missing_file_or_approval(self):
        """Test execute stage is blocked by missing file or approval gate."""
        from main import can_execute_stage

        can_do, reason = can_execute_stage("execute")
        # Execute requires checklist_report.json which doesn't exist
        # OR it requires approval. Either should block it.
        self.assertFalse(can_do)
        # Either missing file or user approval should be in the reason
        self.assertTrue("Missing required file" in reason or "User approval" in reason)


class TestGitCoreFunctions(unittest.TestCase):
    """Test GitCore class functions."""

    def test_git_core_importable(self):
        """Test that GitCore can be imported."""
        from lib.git_core import GitCore, get_git_core

        self.assertIsNotNone(GitCore)
        self.assertIsNotNone(get_git_core)

    def test_git_core_has_required_functions(self):
        """Test that GitCore has all required V8 functions."""
        from lib.git_core import GitCore

        required_functions = [
            "get_patch_id",
            "is_ancestor",
            "get_merge_base",
            "get_remote_refs",
            "get_pr_metadata",
            "calculate_proximity",
            "get_merge_parents",
        ]

        for func_name in required_functions:
            self.assertTrue(
                hasattr(GitCore, func_name),
                f"GitCore missing required function: {func_name}",
            )

    def test_git_core_has_compatibility_functions(self):
        """Test that GitCore has compatibility functions from git_utils.py."""
        from lib.git_core import GitCore

        compatibility_functions = [
            "ref_exists",
            "resolve",
            "commit_distance",
            "merge_commits_between",
            "patch_ids_between",
        ]

        for func_name in compatibility_functions:
            self.assertTrue(
                hasattr(GitCore, func_name),
                f"GitCore missing compatibility function: {func_name}",
            )


class TestMainEntryPoint(unittest.TestCase):
    """Test main.py as entry point."""

    def test_main_module_importable(self):
        """Test that main module can be imported."""
        try:
            import main

            self.assertIsNotNone(main)
        except ImportError as e:
            self.fail(f"Cannot import main module: {e}")

    def test_main_has_stages(self):
        """Test that main module defines STAGES."""
        import main

        self.assertTrue(hasattr(main, "STAGES"))
        self.assertGreater(len(main.STAGES), 0)

    def test_main_has_main_function(self):
        """Test that main module has main function."""
        import main

        self.assertTrue(hasattr(main, "main"))


if __name__ == "__main__":
    unittest.main()
