import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, rel):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "tools"))
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class V74ScaffoldTests(unittest.TestCase):
    def test_config_loader_defaults(self):
        config = load_module("v74_config", "tools/lib/config.py")
        cfg = config.load_config(agent_dir=ROOT)
        self.assertEqual(cfg["execution"]["default_mode"], "analyzer_only")
        self.assertIn("*.lock", cfg["generated_files"]["patterns"])

    def test_failed_rebase_fixture_is_high_risk(self):
        replay = load_module("v74_replay", "tools/lib/replay.py")
        text = (ROOT / "fixtures/failed_rebase/conflicted_status.txt").read_text()
        risk = replay.assess_fixture(text, "fixture")
        self.assertEqual(risk["summary"]["overall_risk"], "high")
        self.assertFalse(risk["summary"]["execution_allowed"])
        self.assertTrue(risk["repository_state"]["active_rebase"])
        self.assertGreater(len(risk["conflicts"]["conflicted_files"]), 0)
        self.assertTrue(
            any(
                x["path"] == "commands_manifest.json"
                for x in risk["generated_file_risks"]
            )
        )

    def test_report_includes_replay_blocker(self):
        reports = load_module("v74_reports", "tools/lib/reports.py")
        inv = {
            "repo": {"git_root": "/tmp/repo", "current_branch": "x", "is_dirty": True},
            "state": {
                "active_rebase": True,
                "active_merge": False,
                "active_cherry_pick": False,
                "conflicted_files": [{"path": "a", "status": "UU"}],
            },
            "targets": {"discovered": []},
        }
        risk = {
            "summary": {
                "overall_risk": "high",
                "execution_allowed": False,
                "primary_reason": "active rebase/conflict state detected",
            },
            "conflicts": {
                "conflicted_files": [
                    {"path": "a", "status": "UU", "conflict_type": "both_modified"}
                ]
            },
            "recommendations": [],
            "generated_file_risks": [],
            "commit_risks": [],
        }
        text = reports.branch_stacking_report(
            inv, risk, {"status": "blocked", "failed_checks": []}
        )
        self.assertIn("Execution is not recommended", text)
        self.assertIn("Do not run Graphite restack", text)

    def test_cli_run_scoped_outputs_in_local_repo(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            shutil.copytree(
                ROOT,
                repo / ".graphite-agent",
                ignore=shutil.ignore_patterns("outputs", "__pycache__"),
            )
            subprocess.run(
                ["git", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
            )
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            (repo / "README.md").write_text("x")
            subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
            subprocess.run(
                ["git", "commit", "-m", "init"],
                cwd=repo,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            rid = "test-run"
            subprocess.run(
                [
                    sys.executable,
                    ".graphite-agent/tools/discover_repo.py",
                    "--local-only",
                    "--run-id",
                    rid,
                ],
                cwd=repo,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                [
                    sys.executable,
                    ".graphite-agent/tools/replay_risk.py",
                    "--local-only",
                    "--run-id",
                    rid,
                ],
                cwd=repo,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                [
                    sys.executable,
                    ".graphite-agent/tools/validate_replay.py",
                    "--run-id",
                    rid,
                ],
                cwd=repo,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                [
                    sys.executable,
                    ".graphite-agent/tools/write_report.py",
                    "--run-id",
                    rid,
                ],
                cwd=repo,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                [
                    sys.executable,
                    ".graphite-agent/tools/build_command_plan.py",
                    "--dry-run",
                    "--run-id",
                    rid,
                ],
                cwd=repo,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            self.assertTrue(
                (
                    repo / ".graphite-agent/outputs/runs/test-run/repo_inventory.json"
                ).exists()
            )
            self.assertTrue(
                (repo / ".graphite-agent/outputs/latest/replay_risk.json").exists()
            )
            plan = json.loads(
                (repo / ".graphite-agent/outputs/latest/command_plan.json").read_text()
            )
            self.assertEqual(plan["mode"], "dry_run")
            self.assertFalse(plan["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
