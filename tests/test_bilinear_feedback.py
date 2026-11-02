import random
import time
import unittest
from liberprimus.bilinear_feedback import affine_chain,decode_prefix,encrypt


class BilinearFeedbackTests(unittest.TestCase):
    def test_every_coefficient_pair(self):
        rng=random.Random(6801);plain=[rng.randrange(29) for _ in range(341)]
        for m in (4,31):
            key=[rng.randrange(29) for _ in range(m)]
            for a in range(1,29):
                for b in range(1,29):
                    cipher=encrypt(plain,key,a,b);queue=key[:];decoded=[]
                    for i,c in enumerate(cipher):
                        p=(a*c+b*queue[i])%29;decoded.append(p);queue.append(p)
                    self.assertEqual(decoded,plain)
                    self.assertEqual(decode_prefix(cipher,plain[:m],a,b),(plain,key))
                    base,coeff=affine_chain(cipher,m,a,b)
                    self.assertEqual([(x+y*plain[i%m])%29 for i,(x,y) in enumerate(zip(base,coeff))],plain)

    def test_histogram_against_literal_screen(self):
        try:import numpy as np
        except ImportError:self.skipTest('Optional NumPy absent')
        import sys
        from pathlib import Path
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
        from bilinear_feedback_factors import period_scores,factor_tables
        from bilinear_feedback_search import factor_score
        rng=np.random.default_rng(6802);cipher=rng.integers(0,29,107).tolist();unigram=rng.normal(size=29)
        for m in (4,13,31):
            scores=period_scores(cipher,m,unigram,time.perf_counter()+20)
            for a in range(1,29):
                for b in range(1,29):
                    base,coeff=map(np.array,affine_chain(cipher,m,a,b))
                    symbols=(base[None,:]+np.arange(29)[:,None]*coeff)%29
                    expected=sum(unigram[symbols[:,r::m]].sum(axis=1).max() for r in range(m))
                    self.assertAlmostEqual(scores[a-1,b-1],expected,places=9)
        lookup=[rng.normal(size=(29,)*k) for k in range(1,4)]
        prefix=rng.integers(0,29,13).tolist();plain,_=decode_prefix(cipher,prefix,17,23)
        factors,*_=factor_tables(cipher,13,17,23,lookup)
        scalar=sum(lookup[min(i,2)][tuple(plain[max(0,i-2):i+1])] for i in range(len(plain)))
        self.assertAlmostEqual(factor_score(factors,prefix),scalar)
