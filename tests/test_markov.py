"""Independent mathematical checks for the diagnostic null, not cipher claims."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np

SPEC = importlib.util.spec_from_file_location("markov_followup", Path(__file__).resolve().parents[1] / "experiments" / "markov_followup.py")
markov = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(markov)


class MarkovChecks(unittest.TestCase):
    def test_closed_form_against_transition_matrix_power(self):
        for m in (3, 29):
            for q in (0, 1/m, 0.0066, 1):
                transition = np.full((m, m), (1-q)/(m-1))
                np.fill_diagonal(transition, q)
                for lag in (1, 2, 3, 16):
                    expected = np.linalg.matrix_power(transition, lag)[0, 0]
                    self.assertAlmostEqual(markov.match_probability(q, lag, m), expected, places=12)

    def test_no_repeat_and_absorbing_extremes(self):
        rng = np.random.default_rng(739)
        nonrepeat = markov.simulate_pages(80, 100, 0, rng)
        self.assertFalse(np.any(nonrepeat[:, 1:] == nonrepeat[:, :-1]))
        absorbing = markov.simulate_pages(80, 100, 1, rng)
        self.assertTrue(np.all(absorbing == absorbing[:, :1]))

    def test_null_sampling_matches_two_step_probability(self):
        chains = markov.simulate_pages(3, 100000, 0.0066, np.random.default_rng(739))
        observed = np.mean(chains[:, 0] == chains[:, 2])
        expected = markov.match_probability(0.0066, 2)
        self.assertLess(abs(observed-expected), 0.002)

    def test_max_t_ranks_and_degenerate_guard(self):
        observed = np.array([4, 7])
        null = np.array([[0, 7], [1, 7], [2, 7], [3, 7]])
        result = markov.symmetric_max_t(observed, null)
        self.assertEqual(result["global_p_plugin"], 2/5)
        self.assertEqual(result["adjusted_p_plugin"][1], 1)
        self.assertEqual(result["active"], [True, False])


if __name__ == "__main__":
    unittest.main()
