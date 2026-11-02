import itertools
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.quadratic_stream import encrypt,decrypt
from liberprimus.decoding import BackoffModel
from quadratic_stream_attack import search
from ngram_arrays import dense_tables


class QuadraticTests(unittest.TestCase):
    def test_reversal_and_period_all_quadratic_coefficients(self):
        values=[(i*i+7*i+11)%29 for i in range(70)]
        for a,b in itertools.product(range(1,29),range(29)):
            c=(a+b)%29;d=(3*a+b)%29
            plain=decrypt(values,a,b,c,d)
            self.assertEqual(encrypt(plain,a,b,c,d),values)
            self.assertEqual(plain[:41],plain[29:])

    def test_vector_grid_matches_independent_scalar(self):
        values=[1,4,28,7,2,0,1];model=BackoffModel([[1,2,3,7,8]*4,[0,1,2,4,28]],order=4)
        grid=([1,5,28],[0,3,28],[0,1,7],range(29));best=-float('inf');count=0
        for a,b,c,d in itertools.product(*grid):
            if not (b or c):continue
            p=[(a*x+b*i*i+c*i+d)%29 for i,x in enumerate(values)]
            best=max(best,model.score(p));count+=1
        score,top,total=search(values,dense_tables(model),time.perf_counter()+10,grid=grid)
        self.assertEqual(total,count);self.assertAlmostEqual(best,score,places=12)
        self.assertEqual(len(top[0]['plaintext_runes']),len(values))

    def test_index_shift_absorbed_by_coefficients(self):
        values=[2,19,0,17,4]
        for offset in range(29):
            direct=[(5*x+7*(i+offset)**2+11*(i+offset)+13)%29 for i,x in enumerate(values)]
            self.assertEqual(direct,decrypt(values,5,7,(11+14*offset)%29,(7*offset**2+11*offset+13)%29))
