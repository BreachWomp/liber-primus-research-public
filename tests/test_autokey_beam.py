import itertools
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from autokey_beam import factor_tables,cycle_beam,SIGNS
from plaintext_autokey_attack import transform
from ngram_arrays import dense_tables,array_scores
from liberprimus.decoding import BackoffModel


class AutokeyBeamTests(unittest.TestCase):
    def test_dense_backoff_tables_match_scalar_orders_one_to_four(self):
        rows=np.array([[0,1,2,4,0,3],[28,27,26,25,24,23]])
        for order in range(1,5):
            model=BackoffModel([[0,1,2,4,0,3,2],[1,2,0,1,2]],order=order)
            lookup=dense_tables(model)
            for row,score in zip(rows,array_scores(rows,lookup)):
                self.assertAlmostEqual(score,model.score(row.tolist()),places=12)
            for table in lookup:self.assertTrue(np.allclose(np.exp(table).sum(axis=-1),1))

    def test_factors_include_boundaries_and_fixed_f_runes(self):
        values=[1,0,0,4,5,6,0,8,9,3,2,1,0,6];key=[4,5,6,7]
        model=BackoffModel([[1,2,0,3,5,0,4,2,1,5,7,8]])
        lookup=dense_tables(model)
        for cs,ks in SIGNS:
            for skip in (False,True):
                plain,_=transform(values,key,cs,ks,skip)
                factors,constant,active,_,_=factor_tables(values,4,cs,ks,skip,lookup)
                prefix=[plain[i] for i in active[:4]]
                score=constant+sum(factors[r,prefix[r],prefix[(r+1)%4],prefix[(r+2)%4]] for r in range(4))
                self.assertAlmostEqual(score/len(values),model.score(plain),places=12)

    def test_unpruned_toy_cycle_matches_exhaustive_global_optimum(self):
        rng=np.random.default_rng(3301017)
        for period in (4,5):
            factors=rng.normal(size=(period,3,3,3))
            expected=max(sum(factors[i,p[i],p[(i+1)%period],p[(i+2)%period]] for i in range(period))
                         for p in itertools.product(range(3),repeat=period))
            actual=cycle_beam(factors,width=3**period,keep=3**period)
            self.assertAlmostEqual(actual[0][1],expected,places=12)
