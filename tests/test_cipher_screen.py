import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("cipher_screen",ROOT/"experiments/cipher_screen.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CipherScreenTests(unittest.TestCase):
    def test_numpy_score_matches_independent_scalar_implementation(self):
        training=[[0,1,2,3,4,5,1,2,3],[2,3,4,4,4]]
        model=MODULE.NGramModel.train(training,order=3,alpha=0.1)
        values=MODULE.np.array([[0,1,2,3],[4,4,4,4],[28,27,26,25]],dtype=MODULE.np.int16)
        got=MODULE.score_rows(values,MODULE.model_table(model))
        for a,b in zip(got,[model.score(row.tolist()) for row in values]):
            self.assertAlmostEqual(a,b,places=12)

    def test_search_family_contains_exact_p56_and_identity(self):
        fixtures=json.loads((ROOT/"known_solutions/fixtures.json").read_text(encoding="utf-8"))
        for ident in ("LP2-56_totient_primes","LP2-57_direct"):
            fixture=next(f for f in fixtures if f["id"]==ident)
            values=MODULE.np.array(MODULE.to_indices(fixture["ciphertext_runes"]),dtype=MODULE.np.int16)
            expected=MODULE.np.array(fixture["expected_indices"],dtype=MODULE.np.int16)
            found=[]
            for rows,recipes in MODULE.recipes(values):
                found += [r for row,r in zip(rows,recipes) if MODULE.np.array_equal(row,expected)]
            self.assertTrue(found,ident)


if __name__=="__main__":
    unittest.main()
