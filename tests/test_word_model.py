import itertools
import math
import unittest
from collections import Counter
from liberprimus.decoding import BackoffModel,replay
from liberprimus.word_model import WordModel,word_selective_decode

class WordModelTests(unittest.TestCase):
    def setUp(self):
        self.model=WordModel(Counter({(0,):5,(1,):3,(1,2):4,(0,2,0):2}),BackoffModel([[0,1,2,0,2,1]],order=3))
    def test_conditional_probability_normalizes(self):
        for length in [1,2]:
            total=sum(math.exp(self.model.logword(word)) for word in itertools.product(range(29),repeat=length))
            self.assertAlmostEqual(total,1,places=12)
        with self.assertRaises(ValueError):self.model.score([0,1],[1])
    def test_exact_dp_matches_exhaustive_masks_and_starts(self):
        values=[0,1,0,2,0];ends=[2,5]
        for repeating,key,starts in [(True,[3,7,11],range(3)),(False,list(range(10)),range(3))]:
            for cs,ks in [(1,-1),(-1,1)]:
                scores=[]
                for start in starts:
                    for mask in itertools.product([False,True],repeat=3):
                        skip=[p for p,yes in zip([0,2,4],mask) if yes]
                        plain=replay(values,key,repeating=repeating,start=start,skip_positions=skip,cipher_sign=cs,key_sign=ks)
                        scores.append(self.model.score(plain,ends))
                actual=word_selective_decode(values,ends,key,self.model,repeating=repeating,starts=starts,cipher_sign=cs,key_sign=ks)
                self.assertAlmostEqual(actual.score,max(scores),places=12)
                self.assertEqual(actual.plaintext,replay(values,key,repeating=repeating,start=actual.start,skip_positions=actual.skip_positions,cipher_sign=cs,key_sign=ks))
