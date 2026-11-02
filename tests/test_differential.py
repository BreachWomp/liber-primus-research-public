from pathlib import Path
import sys
import time
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from differential_affine import recover,encrypt_suffix,scan
from ciphertext_autokey_scan import tables
from liberprimus.decoding import BackoffModel


class DifferentialTests(unittest.TestCase):
    def test_all_affine_parameters_roundtrip(self):
        plain=[1,0,28,3,7,3,1]
        for a in range(1,29):
            for b in range(29):
                self.assertEqual(recover(encrypt_suffix(plain,a,b,17),a,b),plain)

    def test_array_search_matches_scalar_full_grid(self):
        cipher=[7,2,1,5,5,8,28]
        model=BackoffModel([[1,2,3,0,4,1,2,5,4,1]])
        expected=max(model.score(recover(cipher,a,b)) for a in range(1,29) for b in range(29))
        actual,_=scan(np.array([cipher]),tables(model),time.perf_counter()+5)
        self.assertAlmostEqual(float(actual[0]),expected,places=12)
