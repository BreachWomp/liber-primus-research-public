import itertools
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from ciphertext_autokey_scan import tables,scores,scan,SIGNS
from liberprimus.decoding import BackoffModel
from liberprimus.ciphers import autokey


class AutokeyScanTests(unittest.TestCase):
    def test_table_matches_independent_scalar_scoring(self):
        model=BackoffModel([[0,1,2,4,0,3,2],[3,4,5,1,2]])
        values=np.array([[0,1,2,3],[28,0,3,1]],dtype=np.int16)
        result=scores(values,tables(model))
        for row,score in zip(values,result):self.assertAlmostEqual(score,model.score(row.tolist()),places=12)

    def test_scan_matches_exhaustive_scalar_suffixes(self):
        values=[0,1,8,3,4,0,11,8,9,1]
        model=BackoffModel([[0,1,2,4,0,3,2],[3,4,5,1,2]])
        candidates=[]
        for p in range(1,5):
            for cs,ks in SIGNS:
                plain=[(cs*values[i]+ks*values[i-p])%29 for i in range(p,len(values))]
                candidates.append(model.score(plain))
        result,top,count=scan(np.array([values]),tables(model),max_period=4,min_tail=3,keep=True)
        self.assertAlmostEqual(float(result[0]),max(candidates),places=12)
        self.assertEqual(count,16)

    def test_unknown_seed_drops_out_of_ciphertext_feedback_suffix(self):
        plain=[3,1,18,12,4,1,0,23,10,7]
        for key in [[1],[5,7,3],[0,28,10,11]]:
            cipher=autokey(plain,key,decrypt=False,feedback="ciphertext")
            p=len(key)
            self.assertEqual([(cipher[i]-cipher[i-p])%29 for i in range(p,len(cipher))],plain[p:])
