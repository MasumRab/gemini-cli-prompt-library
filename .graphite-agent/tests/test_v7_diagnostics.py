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


class V7DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        self.agent = self.cwd / ".graphite-agent"
        (self.agent / "outputs").mkdir(parents=True)
        shutil.copy(
            FIX / "analysis_snapshot.json", self.agent / "analysis_snapshot.json"
        )
        shutil.copy(FIX / "plan.json", self.agent / "plan.json")
        self.old = Path.cwd()
        os.chdir(self.cwd)
        self.core = load_core()

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_triage_packets(self):
        out = self.core.run_diagnostics(write=True)
        self.assertIn("feature/triage", out["triage_packets"])
        self.assertIn("feature/cross", out["triage_packets"])

    def test_safe_restack_remain_executable(self):
        self.core.run_diagnostics(write=True)
        plan = self.core.load_plan()
        branches = {x["branch"] for x in plan["execution_queue"]}
        self.assertIn("feature/safe", branches)
        self.assertIn("feature/restack", branches)

    def test_question_for_manual_triage(self):
        out = self.core.run_diagnostics(write=True)
        self.assertTrue(
            any(q["branch"] == "feature/triage" for q in out["question_queue"])
        )

    def test_validate_plan_passes(self):
        self.assertEqual(self.core.validation_report()["status"], "pass")

    def test_decision_promotes_branch(self):
        self.core.run_diagnostics(write=True)
        ev = self.core.record_decision(
            "q-000001", "feature/triage", "parent=main", "test"
        )
        self.assertTrue(ev["event_id"].startswith("dec-"))
        plan = json.loads((self.agent / "outputs" / "execution_plan.json").read_text())
        self.assertIn("feature/triage", {x["branch"] for x in plan["execution_queue"]})

    def test_revise_revoke(self):
        self.core.run_diagnostics(write=True)
        first = self.core.record_decision(
            "q-000001", "feature/triage", "parent=main", "first"
        )
        second = self.core.record_decision(
            "q-000001",
            "feature/triage",
            "parent=feature/safe",
            "revise",
            supersedes=first["event_id"],
            event_type="decision_revised",
        )
        self.assertEqual(
            self.core.current_decisions()["feature/triage"]["event_id"],
            second["event_id"],
        )
        self.core.revoke_decision(second["event_id"], "feature/triage", "undo")
        self.assertNotIn("feature/triage", self.core.current_decisions())


if __name__ == "__main__":
    unittest.main()
