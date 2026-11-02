from itertools import combinations,product
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from context_phase_search import optimize,coordinate_key,alternatives
from phase_key_search import replay
from section_key_support import artificial_spans
from liberprimus.decoding import BackoffModel
from ngram_arrays import dense_tables


class ContextPhaseTests(unittest.TestCase):
    def setUp(self):
        self.sequences=[[1,0,2,3,0,4,1,3]*5,[2,4,3,1,0]*5]
        self.cipher=[0,1,2,0,0,3,1,0];self.spans=artificial_spans([0,4,0,4],'test')

    def test_carried_context_dp_matches_all_phases_and_masks(self):
        key=[2,4,1];fs=[0,3,4,7]
        for order in (1,2,4):
            model=BackoffModel(self.sequences,order=order)
            for sign in (-1,1):
                best=-float('inf')
                for p,q in product(range(3),repeat=2):
                    for count in range(5):
                        for skips in combinations(fs,count):
                            best=max(best,model.score(replay(self.cipher,self.spans,key,sign,skips,[0,p,0,q])))
                row=optimize(self.cipher,self.spans,key,sign,model,time.perf_counter()+5)
                self.assertAlmostEqual(best,row['language_score'],places=12)
                self.assertEqual(row['page_phases'][:3],[0,0,0])

    def test_cross_boundary_coordinates_improve_full_context_score(self):
        model=BackoffModel(self.sequences,order=4);key=[5,2,1];phases=[0,0,0,2];skips=[0,4]
        before=model.score(replay(self.cipher,self.spans,key,1,skips,phases))
        new,_=coordinate_key(self.cipher,self.spans,key,1,skips,phases,dense_tables(model),time.perf_counter()+5)
        self.assertGreaterEqual(model.score(replay(self.cipher,self.spans,new,1,skips,phases)),before-1e-12)

    def test_boundary_alternatives_kept_even_when_lower_ranked(self):
        model=BackoffModel(self.sequences,order=4)
        row=optimize(self.cipher,self.spans,[1,2,4],1,model,time.perf_counter()+5)
        alt=alternatives(self.cipher,self.spans,row,model)
        self.assertEqual(len(alt),1);self.assertEqual(alt[0]['position'],4)
        self.assertTrue(alt[0]['ciphertext_identical']);self.assertEqual(alt[0]['changed_positions'],[4])
        self.assertLessEqual(alt[0]['score'],row['score']+1e-12)

    def test_short_pages_and_expired_deadline_rejected(self):
        model=BackoffModel(self.sequences,order=4)
        with self.assertRaises(ValueError):optimize([1,2,3],artificial_spans([3],'test'),[2],1,model,time.perf_counter()+5)
        with self.assertRaises(TimeoutError):optimize(self.cipher,self.spans,[2],1,model,time.perf_counter()-1)
