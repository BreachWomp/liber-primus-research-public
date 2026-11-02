import itertools
from pathlib import Path
import sys
import time
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from liberprimus.decoding import BackoffModel,selective_decode,replay


class ExactDecodingTests(unittest.TestCase):
    def setUp(self):self.model=BackoffModel([[0,1,2,1,3,0,2,4,5],[1,2,1,0]],order=3)

    def test_conditional_probabilities_normalized_even_for_unseen_context(self):
        import math
        for history in [(),(0,),(28,27),(0,1)]:
            self.assertAlmostEqual(sum(math.exp(self.model.logp(history,s)) for s in range(29)),1.0)

    def test_no_ngram_crosses_document_boundary(self):
        model=BackoffModel([[0,1],[2,3]])
        self.assertNotIn((1,),{c for c,v in model.counts.items() if 2 in v})

    def test_dp_matches_exhaustive_subsets_and_all_starts(self):
        data=[0,1,0,2,0,4];fs=[0,2,4]
        for repeat,key,starts in [(True,[2,0,1],range(3)),(False,list(range(12)),range(4))]:
            for cs,ks in itertools.product((-1,1),repeat=2):
                expected=[]
                for flags in itertools.product((False,True),repeat=len(fs)):
                    skips=[f for f,on in zip(fs,flags) if on]
                    for start in starts:
                        plain=replay(data,key,repeating=repeat,start=start,skip_positions=skips,cipher_sign=cs,key_sign=ks)
                        expected.append(self.model.score(plain))
                got=selective_decode(data,key,self.model,repeating=repeat,starts=starts,cipher_sign=cs,key_sign=ks)
                self.assertAlmostEqual(got.score,max(expected),places=12)
                self.assertEqual(got.plaintext,replay(data,key,repeating=repeat,start=got.start,skip_positions=got.skip_positions,cipher_sign=cs,key_sign=ks))

    def test_budget_and_stream_exhaustion(self):
        with self.assertRaises(TimeoutError):selective_decode([1],[1],self.model,deadline=time.perf_counter()-1)
        with self.assertRaises(ValueError):selective_decode([1,2],[1],self.model,repeating=False)


if __name__=="__main__":unittest.main()
