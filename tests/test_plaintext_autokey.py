from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from plaintext_autokey_attack import transform,invert,score_table,fast_score,SIGNS
from liberprimus.ciphers import autokey
from liberprimus.decoding import BackoffModel


class PlaintextAutokeyTests(unittest.TestCase):
    def test_generalized_directions_reencrypt_exactly(self):
        values=[1,0,4,5,8,0,2,13,0];key=[3,2,1]
        for cs,ks in SIGNS:
            for skip in (False,True):
                plain,skips=transform(values,key,cs,ks,skip)
                self.assertEqual(invert(plain,key,cs,ks,skips),values)
                if cs==1 and ks==-1:
                    self.assertEqual(plain,autokey(values,key,feedback="plaintext",skip_positions=skips))

    def test_lookup_score_matches_model(self):
        model=BackoffModel([[1,3,2,0,5,1,6,4]])
        values=[28,1,3,2,4,4,1]
        self.assertAlmostEqual(fast_score(values,score_table(model)),model.score(values),places=12)
