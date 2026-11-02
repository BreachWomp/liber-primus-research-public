import random
import time
import unittest
from liberprimus.affine_feedback import decode_prefix


class DelayTwoTests(unittest.TestCase):
    def test_all_prefix_scores_at_repeated_fourgram_residues(self):
        try:
            import numpy as np
            from delay_two_search import PREFIXES,prefix_scores
        except ImportError:self.skipTest('Optional NumPy runner unavailable')
        rng=np.random.default_rng(7701)
        lookup=[rng.normal(size=(29,)*k) for k in range(1,5)]
        cipher=[7,0,28,13,4,21,2]
        for a,b,c in ((1,1,0),(7,28,19),(14,3,27)):
            scores=prefix_scores(cipher,a,b,c,lookup,time.perf_counter()+30)
            for index,prefix in enumerate(PREFIXES.tolist()):
                plain,_=decode_prefix(cipher,prefix,a,b,c)
                expected=sum(float(lookup[min(i,3)][tuple(plain[max(0,i-3):i+1])]) for i in range(len(cipher)))/len(cipher)
                self.assertAlmostEqual(float(scores[index]),expected,places=12)

    def test_two_rune_roundtrip(self):
        from liberprimus.affine_feedback import encrypt
        rng=random.Random(7702);plain=[rng.randrange(29) for _ in range(66)]
        for a in range(1,29):
            for b in range(1,29):
                c=rng.randrange(29);key=[rng.randrange(29) for _ in range(2)]
                cipher=encrypt(plain,key,a,b,c)
                self.assertEqual(decode_prefix(cipher,plain[:2],a,b,c),(plain,key))
