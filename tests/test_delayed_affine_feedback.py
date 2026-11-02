import random
import time
import unittest
from liberprimus.affine_feedback import affine_chain, decode_prefix, encrypt, reduced_symbol
from liberprimus.bilinear_feedback import affine_chain as zero_chain


class AffineFeedbackTests(unittest.TestCase):
    def test_every_coefficient_and_constant_roundtrip(self):
        rng = random.Random(3300071)
        plain = [rng.randrange(29) for _ in range(41)]
        key = [rng.randrange(29) for _ in range(4)]
        for a in range(1,29):
            for b in range(1,29):
                for c in range(29):
                    cipher = encrypt(plain,key,a,b,c)
                    found, recovered = decode_prefix(cipher,plain[:4],a,b,c)
                    self.assertEqual((found,recovered),(plain,key))

    def test_shift_and_drift_reduction(self):
        rng = random.Random(3300072)
        cipher = [rng.randrange(29) for _ in range(101)]
        for m in (4,13,32):
            for a in (1,2,14,28):
                for b in range(1,29):
                    base1,power = zero_chain(cipher,m,1,b)
                    for c in range(29):
                        t = [rng.randrange(29) for _ in range(m)]
                        reduced = [reduced_symbol(base1[i],power[i],i//m,t[i%m],a,b,c) for i in range(len(cipher))]
                        decoded,_ = decode_prefix(cipher,reduced[:m],a,b,c)
                        self.assertEqual(reduced,decoded)

    def test_invalid(self):
        for args in (([],4,1,1,0),([0]*4,4,0,1,0),([0]*4,4,1,1,29)):
            with self.assertRaises(ValueError):
                affine_chain(*args)

    def test_accelerated_screen_matches_direct(self):
        try:
            import numpy as np
            from affine_feedback_factors import period_scores
        except ImportError:
            self.skipTest('optional NumPy runner unavailable')
        rng = random.Random(3300073)
        values = [rng.randrange(29) for _ in range(49)]
        logp = np.log(np.arange(1,30)/435)
        for m in (4,13,32):
            scores = period_scores(values,m,logp,time.perf_counter()+30)
            for a in (1,7,28):
                for b in (1,2,14,28):
                    for c in range(29):
                        base,power = affine_chain(values,m,a,b,c)
                        literal = sum(max(sum(float(logp[(base[i]+power[i]*p)%29])
                            for i in range(r,len(values),m)) for p in range(29)) for r in range(m))
                        self.assertAlmostEqual(float(scores[a-1,b-1,c]),literal,places=8)

    def test_trigram_factors_include_constant_and_boundaries(self):
        try:
            import numpy as np
            from affine_feedback_factors import factor_tables
            from affine_feedback_search import factor_score
        except ImportError:
            self.skipTest('optional NumPy runner unavailable')
        rng=np.random.default_rng(3300074)
        cipher=rng.integers(0,29,83).tolist()
        lookup=[rng.normal(size=(29,)*k) for k in (1,2,3)]
        for m in (4,13,32):
            for b in (1,2,28):
                prefix=rng.integers(0,29,m).tolist()
                plain,_=decode_prefix(cipher,prefix,7,b,19)
                factors,*_=factor_tables(cipher,m,7,b,19,lookup)
                literal=sum(float(lookup[min(i,2)][tuple(plain[max(0,i-2):i+1])]) for i in range(len(plain)))
                self.assertAlmostEqual(factor_score(factors,prefix),literal,places=8)
