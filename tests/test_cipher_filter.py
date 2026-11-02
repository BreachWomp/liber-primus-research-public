import itertools
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.cipher_filter import decrypt_suffix,encrypt_suffix
from liberprimus.decoding import BackoffModel
from cipher_filter_attack import search
from ngram_arrays import dense_tables


class CipherFilterTests(unittest.TestCase):
    def test_reversible_for_all_invertible_coefficients(self):
        plain=[2,0,14,28,28,4,19]
        for a,c in itertools.product(range(1,29),repeat=2):
            for b,d in [(0,0),(9,28),(28,17)]:
                cipher=encrypt_suffix(plain,a,b,c,d,[8,22])
                self.assertEqual(decrypt_suffix(cipher,a,b,c,d),plain)

    def test_vector_grid_against_scalar_enumeration(self):
        values=[4,22,13,3,18,0,1]
        model=BackoffModel([[1,2,3,18,7,8]*4,[1,2,4,22,0]],order=4)
        grid=([1,5,28],[0,7],[1,3,28],[0,4])
        expected=[]
        for a,b,c,d in itertools.product(*grid):
            if a in (1,28) and c in (1,28) and b==d==0:continue
            plain=decrypt_suffix(values,a,b,c,d)
            expected.append((model.score(plain),plain))
        score,top,count=search(values,dense_tables(model),time.perf_counter()+10,grid=grid)
        self.assertEqual(count,len(expected))
        self.assertAlmostEqual(score,max(s for s,_ in expected),places=12)
        self.assertEqual(len(top[0]['plaintext_runes']),len(values)-2)
