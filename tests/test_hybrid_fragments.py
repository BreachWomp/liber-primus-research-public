from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
import hybrid_fragment_search as hybrid


class HybridFragmentTests(unittest.TestCase):
    def test_union_preserves_best_from_either_branch_and_stable_ties(self):
        for first_score,second_score in ((-2.,-5.),(-5.,-2.),(-2.,-2.)):
            first={'plaintext_runes':'first','score':first_score}
            second={'plaintext_runes':'second','score':second_score}
            with patch.object(hybrid,'constrained',return_value={'top':[first]}) as a, \
                 patch.object(hybrid,'independent',return_value={'top':[second]}) as b, \
                 patch.object(hybrid,'alternatives',return_value=[]) as alternatives:
                result=hybrid.search([1],[],None,None,1.)
            a.assert_called_once();b.assert_called_once()
            self.assertEqual(result['top'][0],first if first_score>=second_score else second)
            self.assertEqual(alternatives.call_args.args[2],result['top'][0])

    def test_exact_pinned_cache_is_used_without_reexecuting_branch(self):
        row={'plaintext_runes':'same','score':-2.}
        cached={'constrained':{'result':{'top':[row]},'output':'prior.json','sha256':'digest'}}
        with patch.object(hybrid,'constrained',side_effect=AssertionError('Repeated completed run')), \
             patch.object(hybrid,'independent',return_value={'top':[row]}) as independent, \
             patch.object(hybrid,'alternatives',return_value=[]):
            result=hybrid.search([1],[],None,None,1.,cached)
        independent.assert_called_once()
        self.assertEqual(result['top'],[row])
        self.assertEqual(result['branches']['constrained'],{'cached_output':'prior.json','cached_sha256':'digest'})
