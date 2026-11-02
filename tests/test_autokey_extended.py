from pathlib import Path
import random
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.autokey_chains import decode_prefix
from plaintext_autokey_attack import invert,transform
from autokey_extended_search import local_scores,factor_score


class ExtendedAutokeyTests(unittest.TestCase):
    def test_scalar_residues_equal_queue_decryption_all_signs(self):
        rng=random.Random(62)
        for m in (4,13,23,31,32):
            cipher=[rng.randrange(29) for _ in range(200)];prefix=[rng.randrange(29) for _ in range(m)]
            for cs in (-1,1):
                for ks in (-1,1):
                    plain,key=decode_prefix(cipher,prefix,cs,ks)
                    self.assertEqual(transform(cipher,key,cs,ks)[0],plain)
                    self.assertEqual(invert(plain,key,cs,ks,[]),cipher)

    def test_local_factor_differences_equal_full_objective(self):
        rng=np.random.default_rng(62)
        for m in (4,13):
            factors=rng.normal(size=(m,29,29,29));prefix=rng.integers(0,29,size=m).tolist()
            for r in range(m):
                local=local_scores(factors,prefix,r);before=factor_score(factors,prefix)
                for q in range(29):
                    changed=prefix[:];changed[r]=q
                    self.assertAlmostEqual(factor_score(factors,changed)-before,local[q]-local[prefix[r]],places=11)
