import itertools
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.offset_feedback import encrypt,decrypt,basis
from liberprimus.decoding import BackoffModel
from offset_feedback_attack import search
from ngram_arrays import dense_tables


class OffsetFeedbackTests(unittest.TestCase):
    def test_reversal_and_basis_all_coefficients(self):
        cipher=[0,12,28,4,4,8]
        for b in range(1,29):
            s,q,t=basis(cipher,b)
            for a,d in itertools.product(range(1,29),repeat=2):
                key=(7*a+3*b+d)%29;plain=decrypt(cipher,a,b,d,key)
                self.assertEqual(encrypt(plain,a,b,d,key),cipher)
                self.assertEqual(plain,[(a*u+plain[0]*v+d*w)%29 for u,v,w in zip(s,q,t)])
            if b==1:self.assertEqual(t,list(range(len(cipher))))

    def test_initial_plaintext_bijection(self):
        for b in range(1,29):
            keys=[pow(b,-1,29)*(x-5*17-9)%29 for x in range(29)]
            self.assertEqual(sorted(keys),list(range(29)))
            for x,key in enumerate(keys):self.assertEqual(decrypt([17],5,b,9,key),[x])

    def test_vector_search_matches_independent_scalar_grid(self):
        values=[4,22,13,3,18,0,1];model=BackoffModel([[1,2,3,18,7,8]*4,[1,2,4,22,0]],order=4)
        grid=([1,5,28],[1,7,28],[1,4,28],range(29));best=-float('inf');count=0
        for a,b,d,key in itertools.product(*grid):
            p=[];previous=key
            for symbol in values:
                previous=(a*symbol+b*previous+d)%29;p.append(previous)
            best=max(best,model.score(p));count+=1
        score,top,actual=search(values,dense_tables(model),time.perf_counter()+10,grid=grid)
        self.assertEqual(actual,count);self.assertAlmostEqual(score,best,places=12)
        self.assertEqual(len(top[0]['plaintext_runes']),len(values))
