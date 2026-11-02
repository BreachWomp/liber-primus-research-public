import random
import unittest
from liberprimus.general_feedback import affine_chain, decode_prefix, encrypt


class GeneralFeedbackTests(unittest.TestCase):
    def test_all_coefficients_queue_and_long_chains(self):
        rng = random.Random(6601)
        plain = [rng.randrange(29) for _ in range(3316)]
        for m in (4, 13, 31, 32):
            key = [rng.randrange(29) for _ in range(m)]
            for a in (-1, 1):
                for b in range(1, 29):
                    cipher = encrypt(plain, key, a, b)
                    queue = key[:]
                    decoded = []
                    for i, c in enumerate(cipher):
                        p = (a*c+b*queue[i]) % 29
                        decoded.append(p)
                        queue.append(p)
                    self.assertEqual(decoded, plain)
                    self.assertEqual(decode_prefix(cipher, plain[:m], a, b), (plain, key))
                    base, coeff = affine_chain(cipher, m, a, b)
                    self.assertTrue(all(0 <= x < 29 for x in base+coeff))
                    self.assertEqual([(x+y*plain[i % m]) % 29 for i, (x, y) in enumerate(zip(base, coeff))], plain)

    def test_reject_invalid_family(self):
        for m, a, b in ((0, 1, 1), (4, 0, 1), (4, 1, 0), (4, 1, 29)):
            with self.assertRaises(ValueError):
                affine_chain([1]*8, m, a, b)
        with self.assertRaises(ValueError):
            decode_prefix([1], [1, 2], 1, 2)

    def test_trigram_factors_and_coordinate_scores(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest('Optional NumPy runner absent')
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'experiments'))
        from general_feedback_factors import factor_tables
        from general_feedback_search import local_scores, factor_score
        rng = np.random.default_rng(6602)
        lookup = [rng.normal(size=(29,)*k) for k in range(1, 4)]
        cipher = rng.integers(0, 29, 79).tolist()
        for m, a, b in ((4, 1, 2), (13, -1, 27), (31, 1, 14)):
            prefix = rng.integers(0, 29, m).tolist()
            factors, _, _, _, _ = factor_tables(cipher, m, a, b, lookup)
            def score(p):
                decoded, _ = decode_prefix(cipher, p, a, b)
                return sum(lookup[min(2, i)][tuple(decoded[max(0, i-2):i+1])] for i in range(len(cipher)))
            baseline = score(prefix)
            self.assertAlmostEqual(factor_score(factors, prefix), baseline)
            for residue in (0, m-1):
                local = local_scores(factors, prefix, residue)
                for symbol in range(29):
                    trial = prefix[:]
                    trial[residue] = symbol
                    self.assertAlmostEqual(local[symbol]-local[prefix[residue]], score(trial)-baseline)


if __name__ == '__main__':
    unittest.main()
