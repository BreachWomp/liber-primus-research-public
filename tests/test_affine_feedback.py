import itertools
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from affine_plaintext_feedback import encrypt,decrypt,parameters,search
from ngram_arrays import dense_tables
from liberprimus.decoding import BackoffModel

class AffineFeedbackTests(unittest.TestCase):
    def test_grid_excludes_prior_sign_pairs_and_is_invertible(self):
        self.assertEqual(len(parameters()),780)
        self.assertFalse(set(parameters()) & {(1,1),(1,28),(28,1),(28,28)})
        plain=[3,1,0,0,7,19,28,8,2]
        for a,b in parameters():
            for key in (0,17,28):
                self.assertEqual(decrypt(encrypt(plain,a,b,key),a,b,key),plain)

    def test_vector_search_matches_independent_exhaustive_recurrence(self):
        cipher=[7,2,19,0,28,4]
        model=BackoffModel([[1,0,3,5,2,19],[4,3,2,1,0]],order=4)
        expected=max(model.score(decrypt(cipher,a,b,key)) for a,b in parameters() for key in range(29))
        best,top,total=search(cipher,dense_tables(model),time.perf_counter()+30)
        self.assertEqual(total,22620)
        self.assertAlmostEqual(best,expected,places=12)
        for row in top:
            r=row['recipe']
            self.assertEqual(encrypt(decrypt(cipher,r['a'],r['b'],r['initial_key']),r['a'],r['b'],r['initial_key']),cipher)
