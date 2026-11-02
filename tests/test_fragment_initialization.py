from itertools import product
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.decoding import BackoffModel
from ngram_arrays import dense_tables
from fragment_initialization_search import phase_fit, unigram_key
from section_key_support import artificial_spans


class FragmentInitializationTests(unittest.TestCase):
    def setUp(self):
        self.sequences=[[1,2,3,4,1,3,2]*4,[4,3,5,1,2]*4]
        self.values=[1,3,2,5,4,3,2,1,6]
        self.spans=artificial_spans([4,5],'test')

    def score(self,key,sign,phases,model):
        total=0.
        for span,phase in zip(self.spans,phases):
            part=self.values[span['start']:span['end']]
            total+=len(part)*model.score([(sign*c+key[(i+phase)%len(key)])%29 for i,c in enumerate(part)])
        return total/len(self.values)

    def test_vector_phases_equal_independent_scalar_enumeration_all_orders(self):
        for order in (1,2,4):
            model=BackoffModel(self.sequences,order=order);lookup=dense_tables(model)
            for sign in (1,-1):
                key=[5,2,3]
                expected=max(self.score(key,sign,phases,model) for phases in product(range(3),repeat=2))
                row=phase_fit(self.values,self.spans,key,sign,lookup,time.perf_counter()+5)
                self.assertAlmostEqual(row['language_score'],expected,places=12)
                self.assertEqual(row['page_phases'][0],0)
                self.assertAlmostEqual(self.score(row['key'],sign,row['page_phases'],model),expected,places=12)

    def test_unigram_joint_key_matches_exhaustive_key_search(self):
        model=BackoffModel(self.sequences,order=1);lookup=dense_tables(model);phases=[0,1]
        for sign in (1,-1):
            key=unigram_key(self.values,self.spans,phases,2,sign,lookup)
            expected=max(self.score(list(k),sign,phases,model) for k in product(range(29),repeat=2))
            self.assertAlmostEqual(self.score(key,sign,phases,model),expected,places=12)

    def test_phase_pool_rejects_F_and_checks_deadline(self):
        lookup=dense_tables(BackoffModel(self.sequences,order=1))
        with self.assertRaises(ValueError):phase_fit([0],artificial_spans([1],'test'),[2],1,lookup,time.perf_counter()+5)
        with self.assertRaises(TimeoutError):phase_fit(self.values,self.spans,[2],1,lookup,time.perf_counter()-1)
