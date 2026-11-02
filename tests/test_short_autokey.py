from pathlib import Path
import sys
import time
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from short_seed_autokey import affine_chain,prefix_block,scan,SIGNS
from plaintext_autokey_attack import transform
from ciphertext_autokey_scan import tables
from liberprimus.decoding import BackoffModel


class ShortAutokeyTests(unittest.TestCase):
    def test_affine_recurrence_matches_scalar_for_every_direction(self):
        values=[1,3,0,8,2,0,6,11,5];key=[7,11,23]
        for cs,ks in SIGNS:
            expected,_=transform(values,key,cs,ks)
            base,coeff=affine_chain(values,len(key),cs,ks)
            actual=(np.array(expected[:3])[np.arange(len(values))%3]*coeff+base)%29
            self.assertEqual(actual.tolist(),expected)

    def test_prefix_enumeration_is_bijective(self):
        rows=prefix_block(0,29**3,3)
        self.assertEqual(len(set(map(tuple,rows.tolist()))),29**3)
        self.assertEqual(rows.min(),0);self.assertEqual(rows.max(),28)

    def test_full_one_rune_search_matches_scalar_keys(self):
        values=[1,0,4,2,5,1,7]
        model=BackoffModel([[1,2,0,3,1,5,4,2]])
        expected=[]
        for key in range(29):
            for cs,ks in SIGNS:
                for skip in (False,True):
                    plain,_=transform(values,[key],cs,ks,skip)
                    expected.append(model.score(plain))
        actual,_,tasks=scan(values,tables(model),time.perf_counter()+10,max_period=1,batch=7)
        self.assertAlmostEqual(actual,max(expected),places=12)
        self.assertEqual(tasks,29*8)
