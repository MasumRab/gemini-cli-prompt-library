import json, shutil, tempfile, unittest, importlib.util, sys, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CORE=ROOT/'tools'/'agent_core.py'; FIX=ROOT/'fixtures'/'v64'
def load_core():
    spec=importlib.util.spec_from_file_location('agent_core', CORE); mod=importlib.util.module_from_spec(spec); sys.modules['agent_core']=mod; spec.loader.exec_module(mod); return mod
class V73Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.cwd=Path(self.tmp.name); self.agent=self.cwd/'.graphite-agent'; (self.agent/'outputs').mkdir(parents=True); shutil.copy(FIX/'analysis_snapshot.json', self.agent/'analysis_snapshot.json'); shutil.copy(FIX/'plan.json', self.agent/'plan.json'); self.old=Path.cwd(); os.chdir(self.cwd); self.core=load_core()
    def tearDown(self): os.chdir(self.old); self.tmp.cleanup()
    def test_diagnostics(self):
        self.core.analyse_outputs(); tri=self.core.rj(self.agent/'outputs'/'triage_packets.json',{}); self.assertIn('feature/science-a', tri)
    def test_target_discovery(self): self.assertIn('scientific', self.core.discover_targets()['candidates'])
    def test_target_matrix(self): self.assertIn('feature/science-a', self.core.target_analyse())
    def test_root_health(self): self.assertEqual(self.core.root_health()['scientific']['health'], 'stale')
    def test_stack_blocks_stale_root(self): self.core.root_health(); self.assertFalse(self.core.stack_order()['targets']['scientific']['execution_allowed'])
if __name__=='__main__': unittest.main()
