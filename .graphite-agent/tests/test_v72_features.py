import json, shutil, tempfile, unittest, importlib.util, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools" / "agent_core.py"
FIX_V72 = ROOT / "fixtures" / "v72"
FIX_V64 = ROOT / "fixtures" / "v64"


def load_core():
    spec = importlib.util.spec_from_file_location("agent_core", CORE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["agent_core"] = mod
    spec.loader.exec_module(mod)
    return mod


class V72TargetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        self.agent = self.cwd / ".graphite-agent"
        (self.agent / "outputs").mkdir(parents=True)
        shutil.copy(FIX_V72 / "analysis_snapshot.json", self.agent / "analysis_snapshot.json")
        shutil.copy(FIX_V72 / "plan.json", self.agent / "plan.json")
        self.old = Path.cwd()
        os.chdir(self.cwd)
        self.core = load_core()

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_target_matrix_generated(self):
        branches = self.core.target_analyse()
        self.assertIn("feature/merge-conflict-resolution", branches)

    def test_same_target_merge_diagnosed(self):
        branches = self.core.target_analyse()
        merge_branch = branches.get("feature/merge-conflict-resolution", {})
        # target_analyse reports target_confirmed when declared_base matches inferred root_branch
        self.assertEqual(
            merge_branch.get("diagnostic_category"),
            "target_confirmed"
        )

    def test_cross_root_blocked(self):
        # v72 has single-root, but test that cross-root branches are excluded from stacks
        self.core.root_health()
        stack = self.core.stack_order()
        for target_name, target_data in stack.get("targets", {}).items():
            for stack in target_data.get("stacks", []):
                for branch in stack.get("branches", []):
                    self.assertNotEqual(branch.get("branch"), "feature/cross")


class V72MergeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        self.agent = self.cwd / ".graphite-agent"
        (self.agent / "outputs").mkdir(parents=True)
        shutil.copy(FIX_V72 / "analysis_snapshot.json", self.agent / "analysis_snapshot.json")
        shutil.copy(FIX_V72 / "plan.json", self.agent / "plan.json")
        self.old = Path.cwd()
        os.chdir(self.cwd)
        self.core = load_core()

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_merge_conflict_diagnosed(self):
        self.core.analyse_outputs()
        tri = self.core.rj(self.agent / "outputs" / "triage_packets.json", {})
        merge_branch = tri.get("feature/merge-conflict-resolution")
        self.assertIsNotNone(merge_branch)
        self.assertEqual(merge_branch.get("diagnostic_category"), "in_target_conflict_resolution_merge")

    def test_merge_conflict_blocked_in_stack(self):
        self.core.root_health()
        stack = self.core.stack_order()
        # feature/merge-conflict-resolution should not appear in any executable stack
        for target_name, target_data in stack.get("targets", {}).items():
            for st in target_data.get("stacks", []):
                branches = [b.get("branch") for b in st.get("branches", [])]
                self.assertNotIn("feature/merge-conflict-resolution", branches)


class V72StaleRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        self.agent = self.cwd / ".graphite-agent"
        (self.agent / "outputs").mkdir(parents=True)
        shutil.copy(FIX_V72 / "analysis_snapshot.json", self.agent / "analysis_snapshot.json")
        shutil.copy(FIX_V72 / "plan.json", self.agent / "plan.json")
        self.old = Path.cwd()
        os.chdir(self.cwd)
        self.core = load_core()

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_root_health_blocks_stale_root(self):
        # v72 single-root with multiple blocked branches should be stale
        root_health = self.core.root_health()
        # With v72 fixtures, main has blocked_merge_commits + manual_triage + cross_root_conflict
        self.assertEqual(root_health.get("main", {}).get("health"), "stale")
        self.assertFalse(root_health.get("main", {}).get("execution_allowed"))


if __name__ == "__main__":
    unittest.main()
