from itertools import combinations
from pathlib import Path
import sys
import time
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.decoding import BackoffModel
from section_key_support import artificial_spans
from reset_key_search import factors_at,optimize,replay,coordinate_key
from ngram_arrays import dense_tables


class ResetKeyTests(unittest.TestCase):
    def setUp(self):
        self.model=BackoffModel([[1,2,0,3,1,0,2,4]*5,[0,1,4,2,3]*4],order=4)

    def test_common_phase_schedule_matches_exhaustive_masks(self):
        values=[0,1,0,2,0,4,0];spans=artificial_spans([3,0,4],'test');key=[1,3]
        fs=[i for i,x in enumerate(values) if x==0];best=-float('inf')
        for phase in range(len(key)):
            oriented=key[phase:]+key[:phase]
            for count in range(len(fs)+1):
                for skips in combinations(fs,count):
                    plain=replay(values,spans,oriented,-1,skips)
                    score=sum(self.model.score(plain[s['start']:s['end']])*(s['end']-s['start']) for s in spans if s['end']>s['start'])/len(values)
                    best=max(best,score)
        got=optimize(values,spans,key,-1,self.model,time.perf_counter()+5,True)
        self.assertAlmostEqual(best,got['language_score'],places=12)

    def test_array_factors_reset_at_each_page(self):
        plain=np.array([0,1,2,3,4,2,1]);starts=np.array([0,0,0,3,3,3,3]);lookup=dense_tables(self.model)
        rows=np.tile(plain,(29,1));rows[:,[1,4]]=np.arange(29)[:,None]
        got=factors_at(rows,np.arange(7),lookup,starts).sum(axis=1)
        for row,value in zip(rows,got):
            expected=3*self.model.score(row[:3].tolist())+4*self.model.score(row[3:].tolist())
            self.assertAlmostEqual(expected,float(value),places=12)

    def test_shared_coordinate_update_is_monotone(self):
        values=[0,1,2,0,3,4,0,2];spans=artificial_spans([4,0,4],'test');key=[2,5];skips=[0,6]
        def score(k):
            p=replay(values,spans,k,1,skips)
            return self.model.score(p[:4])+self.model.score(p[4:])
        updated,_=coordinate_key(values,spans,key,1,skips,dense_tables(self.model),time.perf_counter()+5)
        self.assertGreaterEqual(score(updated),score(key)-1e-12)
