import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest

SPEC=importlib.util.spec_from_file_location("sampler_audit",Path(__file__).resolve().parents[1]/"experiments/sampler_audit.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SamplerAuditTests(unittest.TestCase):
    def test_exact_stationarity_and_target_invariants(self):
        states,adjacency,jump,proposal,components=MODULE.build()
        self.assertEqual(len(states),12)
        self.assertEqual(len(components),1)
        for state in states:
            self.assertEqual(sorted(state),[0,0,1,1,2])
            self.assertEqual(MODULE.doublets(state),1)
        uniform=[Fraction(1,12)]*12
        degrees=[len(n) for n in adjacency]
        stationary=[Fraction(d,sum(degrees)) for d in degrees]
        self.assertEqual(MODULE.multiply(uniform,proposal),uniform)
        self.assertNotEqual(MODULE.multiply(uniform,jump),uniform)
        self.assertEqual(MODULE.multiply(stationary,jump),stationary)
        self.assertEqual(sorted(set(degrees)),[1,2,4])


if __name__=="__main__":unittest.main()
