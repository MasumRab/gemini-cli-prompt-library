import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from graphite_agent.core import TopologyAuditEngine, Config, Policy
class G: pass
class T(unittest.TestCase):
    def test_cycle_canonical(self):
        e=TopologyAuditEngine(Config(['main'],'main'),G(),Policy())
        self.assertEqual(e.canonicalize_cycle(['b','a','c']), ['a','b','c'])
    def test_kahn_invalid(self):
        e=TopologyAuditEngine(Config(['main'],'main'),G(),Policy())
        ok,_=e.kahn(['a','b'], [('a','b'),('b','a')])
        self.assertFalse(ok)
if __name__=='__main__': unittest.main()
