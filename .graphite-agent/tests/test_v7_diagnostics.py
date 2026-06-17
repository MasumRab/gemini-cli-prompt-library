import json, shutil, tempfile, unittest, importlib.util, sys, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CORE=ROOT/'tools'/'agent_core.py'; FIX=ROOT/'fixtures'/'v64'
def load_core():
    spec=importlib.util.spec_from_file_location('agent_core', CORE); mod=importlib.util.module_from_spec(spec); sys.modules['agent_core']=mod; spec.loader.exec_module(mod); return mod
def read_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default
class V7DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.cwd=Path(self.tmp.name); self.agent=self.cwd/'.graphite-agent'; (self.agent/'outputs').mkdir(parents=True); shutil.copy(FIX/'analysis_snapshot.json', self.agent/'outputs'/'analysis_snapshot.json'); shutil.copy(FIX/'plan.json', self.agent/'plan.json'); self.old=Path.cwd(); os.chdir(self.cwd); self.core=load_core()
    def tearDown(self): os.chdir(self.old); self.tmp.cleanup()
    def test_triage_packets(self):
        out=self.core.run_diagnostics(write=True); self.assertIn('feature/triage', out['triage_packets']); self.assertIn('feature/cross', out['triage_packets'])
    def test_safe_restack_remain_executable(self):
        self.core.run_diagnostics(write=True); plan=self.core.load_plan(); branches={x['branch'] for x in plan['execution_queue']}; self.assertIn('feature/safe', branches); self.assertIn('feature/restack', branches)
    def test_question_for_manual_triage(self):
        out=self.core.run_diagnostics(write=True); self.assertTrue(any(q['branch']=='feature/triage' for q in out['question_queue']))
    def test_validate_plan_passes(self): self.assertEqual(self.core.validation_report()['status'], 'pass')
    def test_decision_promotes_branch(self):
        self.core.run_diagnostics(write=True); ev=self.core.record_decision('q-000001','feature/triage','parent=main','test'); self.assertTrue(ev['event_id'].startswith('dec-')); plan=json.loads((self.agent/'outputs'/'execution_plan.json').read_text()); self.assertIn('feature/triage', {x['branch'] for x in plan['execution_queue']})
    def test_revise_revoke(self):
        self.core.run_diagnostics(write=True); first=self.core.record_decision('q-000001','feature/triage','parent=main','first'); second=self.core.record_decision('q-000001','feature/triage','parent=feature/safe','revise', supersedes=first['event_id'], event_type='decision_revised'); self.assertEqual(self.core.current_decisions()['feature/triage']['event_id'], second['event_id']); self.core.revoke_decision(second['event_id'],'feature/triage','undo'); self.assertNotIn('feature/triage', self.core.current_decisions())

class V72TargetTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.cwd=Path(self.tmp.name)
        self.agent=self.cwd/'.graphite-agent'
        (self.agent/'outputs').mkdir(parents=True)
        shutil.copy(FIX/'analysis_snapshot.json', self.agent/'outputs'/'analysis_snapshot.json')
        shutil.copy(FIX/'plan.json', self.agent/'outputs'/'execution_plan.json')
        self.old=Path.cwd()
        os.chdir(self.cwd)
        self.core=load_core()
    def tearDown(self): os.chdir(self.old); self.tmp.cleanup()
    def test_target_matrix_generated(self):
        self.core.run_diagnostics(write=True)
        import subprocess
        subprocess.run(['python', str(ROOT/'tools'/'target_analyse.py')], capture_output=True, cwd=self.cwd)
        matrix_path = self.cwd/'.graphite-agent'/'outputs'/'target_matrix.json'
        self.assertTrue(matrix_path.exists())
    def test_same_target_merge_diagnosed(self):
        self.core.run_diagnostics(write=True)
        import subprocess
        subprocess.run(['python', str(ROOT/'tools'/'target_analyse.py')], capture_output=True, cwd=self.cwd)
        matrix = read_json((self.cwd/'.graphite-agent'/'outputs'/'target_matrix.json'), {})
        self.assertIn('diagnostic_category', matrix.get('branches', {}).get('feature/triage', {}))
    def test_cross_root_blocked(self):
        self.core.run_diagnostics(write=True)
        import subprocess
        subprocess.run(['python', str(ROOT/'tools'/'stack_order.py')], capture_output=True, cwd=self.cwd)
        stack = read_json((self.cwd/'.graphite-agent'/'outputs'/'stack_order.json'), {})
        main_stacks = stack.get('targets', {}).get('main', {}).get('stacks', [])
        blocked_branches = [b.get('branch') for s in main_stacks for b in s.get('branches', [])]
        self.assertNotIn('feature/cross', blocked_branches)

class V72MergeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.cwd=Path(self.tmp.name)
        self.agent=self.cwd/'.graphite-agent'
        (self.agent/'outputs').mkdir(parents=True)
        v72_fix = ROOT/'fixtures'/'v72'
        shutil.copy(v72_fix/'analysis_snapshot.json', self.agent/'outputs'/'analysis_snapshot.json')
        shutil.copy(v72_fix/'plan.json', self.agent/'outputs'/'execution_plan.json')
        self.old=Path.cwd()
        os.chdir(self.cwd)
        self.core=load_core()
    def tearDown(self): os.chdir(self.old); self.tmp.cleanup()
    def test_merge_conflict_diagnosed(self):
        self.core.run_diagnostics(write=True)
        import subprocess
        subprocess.run(['python', str(ROOT/'tools'/'target_analyse.py')], capture_output=True, cwd=self.cwd)
        matrix = read_json((self.cwd/'.graphite-agent'/'outputs'/'target_matrix.json'), {})
        diag = matrix.get('branches', {}).get('feature/merge-conflict-resolution', {}).get('diagnostic_category')
        self.assertEqual(diag, 'in_target_conflict_resolution_merge')
    def test_merge_conflict_blocked_in_stack(self):
        self.core.run_diagnostics(write=True)
        import subprocess
        subprocess.run(['python', str(ROOT/'tools'/'stack_order.py')], capture_output=True, cwd=self.cwd)
        stack = read_json((self.cwd/'.graphite-agent'/'outputs'/'stack_order.json'), {})
        main_data = stack.get('targets', {}).get('main', {})
        self.assertFalse(main_data.get('execution_allowed', True))

class V72StaleRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.cwd=Path(self.tmp.name)
        self.agent=self.cwd/'.graphite-agent'
        (self.agent/'outputs').mkdir(parents=True)
        v72_fix = ROOT/'fixtures'/'v72'
        shutil.copy(v72_fix/'analysis_snapshot.json', self.agent/'outputs'/'analysis_snapshot.json')
        shutil.copy(v72_fix/'plan.json', self.agent/'outputs'/'execution_plan.json')
        self.old=Path.cwd()
        os.chdir(self.cwd)
        self.core=load_core()
    def tearDown(self): os.chdir(self.old); self.tmp.cleanup()
    def test_root_health_blocks_stale_root(self):
        self.core.run_diagnostics(write=True)
        import subprocess
        subprocess.run(['python', str(ROOT/'tools'/'root_health.py')], capture_output=True, cwd=self.cwd)
        health = read_json((self.cwd/'.graphite-agent'/'outputs'/'root_health.json'), {})
        roots = health.get('roots', {})
        for root, data in roots.items():
            if data.get('health') == 'stale':
                self.assertTrue(data.get('execution_allowed') == False)
                break

if __name__=='__main__': unittest.main()