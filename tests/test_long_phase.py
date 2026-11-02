from itertools import combinations
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from long_phase_search import page_fragments
from pooled_long_key_search import pooled_fragments
from phase_key_search import optimize
from section_key_support import artificial_spans
from liberprimus.decoding import BackoffModel


class LongPhaseTests(unittest.TestCase):
    def test_fragments_split_at_page_boundaries_and_retain_empty_page(self):
        values=[1]*20+[2]*20+[0]+[3]*17;spans=artificial_spans([20,0,20,18],'test')
        pool,fragments,ranges=page_fragments(values,spans)
        self.assertEqual(ranges,[(0,20),(20,40),(41,58)])
        self.assertEqual(len(pool),57)
        self.assertEqual(spans[1]['runes'],0)
        for a,b in ranges:self.assertTrue(any(s['start']<=a<b<=s['end'] for s in spans))

    def test_single_page_pool_matches_frozen_initializer(self):
        values=[1]*31+[0]+[2]*19+[0]+[3]*256+[4]*12
        self.assertEqual(page_fragments(values,artificial_spans([len(values)],'test')),pooled_fragments(values))

    def test_length31_phase_and_mask_optimum_matches_scalar_enumeration(self):
        model=BackoffModel([[1,2,0,3,4]*10,[0,4,1,2]*10],order=4)
        key=[i%29 for i in range(31)];values=[0,1,0,2,0,4,0,3]
        spans=artificial_spans([4,0,4],'test');best=0.
        for span in spans:
            part=values[span['start']:span['end']]
            if not part:continue
            fs=[i for i,c in enumerate(part) if c==0];score=-float('inf')
            for phase in range(31):
                for count in range(len(fs)+1):
                    for skips in combinations(fs,count):
                        plain=[];cursor=phase
                        for i,c in enumerate(part):
                            if i in skips:plain.append(0)
                            else:plain.append((-c+key[cursor%31])%29);cursor+=1
                        score=max(score,model.score(plain))
            best+=score*len(part)
        result=optimize(values,spans,key,-1,model,time.perf_counter()+5)
        self.assertAlmostEqual(best/len(values),result['language_score'],places=12)
        self.assertEqual(result['page_phases'][0],0)
        self.assertEqual(result['page_phases'][1],0)
