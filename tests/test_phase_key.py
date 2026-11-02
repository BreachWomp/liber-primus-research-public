from itertools import combinations,product
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.decoding import BackoffModel
from section_key_support import artificial_spans
from phase_key_search import replay,optimize,coordinate_key
from ngram_arrays import dense_tables


class PagePhaseTests(unittest.TestCase):
    def setUp(self):
        self.model=BackoffModel([[1,2,0,3,1,0,2,4]*5,[0,1,4,2,3]*4],order=4)
        self.values=[0,1,0,2,0,4,0];self.spans=artificial_spans([0,3,0,4],'test')

    def score(self,plain):
        return (3*self.model.score(plain[:3])+4*self.model.score(plain[3:]))/7

    def test_all_page_phases_and_masks_match_enumeration(self):
        fs=[0,2,4,6];best=-float('inf');key=[1,3]
        for a,b in product(range(2),repeat=2):
            for n in range(5):
                for skips in combinations(fs,n):
                    best=max(best,self.score(replay(self.values,self.spans,key,-1,skips,[0,a,0,b])))
        got=optimize(self.values,self.spans,key,-1,self.model,time.perf_counter()+5)
        self.assertAlmostEqual(best,got['language_score'],places=12)
        self.assertEqual(got['page_phases'][1],0)
        self.assertEqual(got['page_phases'][0],0)
        self.assertEqual(got['page_phases'][2],0)

    def test_global_rotation_leaves_plaintext_invariant(self):
        key=[2,5,7];phases=[0,1,0,2];skips=[0,4]
        plain=replay(self.values,self.spans,key,1,skips,phases)
        rotated=key[1:]+key[:1];shifted=[0,0,0,1]
        self.assertEqual(plain,replay(self.values,self.spans,rotated,1,skips,shifted))

    def test_shared_coordinate_with_different_page_phases(self):
        key=[2,5,7];phases=[0,0,0,2];skips=[0,4]
        before=self.score(replay(self.values,self.spans,key,1,skips,phases))
        after,_=coordinate_key(self.values,self.spans,key,1,skips,phases,dense_tables(self.model),time.perf_counter()+5)
        self.assertGreaterEqual(self.score(replay(self.values,self.spans,after,1,skips,phases)),before-1e-12)
