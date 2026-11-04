import json, shutil, tempfile, unittest, importlib.util, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools" / "agent_core.py"
FIX = ROOT / "fixtures" / "v64"


def load_core():
    spec = importlib.util.spec_from_file_location("agent_core", CORE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["agent_core"] = mod
    spec.loader.exec_module(mod)
    return mod


class AgentCoreHelperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        self.agent = self.cwd / ".graphite-agent"
        (self.agent / "outputs").mkdir(parents=True)
        shutil.copy(FIX / "analysis_snapshot.json", self.agent / "analysis_snapshot.json")
        shutil.copy(FIX / "plan.json", self.agent / "plan.json")
        self.old = Path.cwd()
        os.chdir(self.cwd)
        self.core = load_core()

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_nodes_helper_returns_branch_graph(self):
        s = self.core.snap()
        nodes = self.core.nodes(s)
        self.assertIn("feature/safe", nodes)
        self.assertIn("feature/science-a", nodes)

    def test_nodes_helper_falls_back_to_branch_state(self):
        s = {"branch_state": {"feature/x": {"status": "safe"}}}
        nodes = self.core.nodes(s)
        self.assertIn("feature/x", nodes)

    def test_snap_reads_from_outputs_then_agent_dir(self):
        s = self.core.snap()
        self.assertIn("branch_graph", s)

    def test_plan_reads_from_outputs_then_agent_dir(self):
        p = self.core.plan()
        self.assertIn("execution_queue", p)

    def test_summary_counts(self):
        s = self.core.snap()
        p = self.core.plan()
        summary = self.core.summary(s, p)
        self.assertIn("branches_total", summary["counts"])
        self.assertGreater(summary["counts"]["branches_total"], 0)

    def test_triage_packets_blocks_non_executable(self):
        s = self.core.snap()
        rel = self.core.relationship_graph(s)
        tri = self.core.triage_packets(s, rel)
        self.assertIn("feature/science-a", tri)
        self.assertIn("feature/science-b", tri)

    def test_questions_generates_options(self):
        triage = {
            "feature/x": {
                "status": "manual_triage",
                "root_branch": "main",
                "diagnostic_category": "manual_triage",
            }
        }
        qs = self.core.questions(triage)
        self.assertEqual(len(qs), 1)
        self.assertIn("leave_triage", qs[0]["options"])

    def test_relationship_graph_uses_lib_when_missing(self):
        s = self.core.snap()
        rel = self.core.relationship_graph(s)
        self.assertIn("edges", rel)

    def test_analyse_outputs_returns_summary(self):
        result = self.core.analyse_outputs()
        self.assertIn("branches_total", result["counts"])


if __name__ == "__main__":
    unittest.main()
