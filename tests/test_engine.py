"""Synthetic controls isolate mathematics from uncertain historical hypotheses."""

import math
import unittest
from itertools import count, islice
from random import Random

from liberprimus import alphabet, ciphers, crosspage, known_plaintext, search, stats, transpositions
from liberprimus.scoring import NGramModel


class AlphabetTests(unittest.TestCase):
    def test_canonical_order_and_explicit_aliases(self):
        self.assertEqual(len(set(alphabet.RUNES)), 29)
        self.assertEqual(alphabet.to_indices(alphabet.RUNES), list(range(29)))
        self.assertEqual(alphabet.to_runes(range(29)), alphabet.RUNES)
        self.assertEqual(alphabet.to_indices("ᛂ ᛜ"), [11, 21])
        self.assertEqual(alphabet.transliterate([0, 2, 11, 28]), "FTHJEA")
        self.assertEqual(alphabet.gematria_sum(range(29)), sum(alphabet.PRIMES))

    def test_unknown_symbols_are_not_silently_discarded(self):
        for text in ("ᚠA", "ᚠ0", "ᛮ", "🦗"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                alphabet.to_indices(text)
        with self.assertRaises(ValueError):
            alphabet.to_indices("ᚠ ᚢ", ignore_separators=False)
        for values in ([29], [-1], [True], [2.0]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                alphabet.to_runes(values)

    def test_render_and_latin_convention(self):
        self.assertEqual(alphabet.render_like("ᚠ•ᚢ\nᚦ", [8, 18, 20]), "ᚻ•ᛖ\nᛚ")
        self.assertEqual(alphabet.render_like("ᚠ-ᚢ", [2, 18], latin=True), "TH-E")
        with self.assertRaises(ValueError):
            alphabet.render_like("ᚠ-ᚢ", [1])
        self.assertEqual(alphabet.latin_to_indices("DIVINITY"), [23, 10, 1, 10, 9, 10, 16, 26])
        self.assertEqual(alphabet.latin_to_indices("THING"), [2, 21])
        self.assertEqual(alphabet.latin_to_indices("THING", digraphs=False), [16, 8, 10, 9, 6])
        with self.assertRaises(ValueError):
            alphabet.latin_to_indices("Q")


class CipherTests(unittest.TestCase):
    def test_affine_all_invertible_multipliers(self):
        values = list(range(29))
        for a in range(1, 29):
            for b in (0, 7, 28, -3):
                cipher = ciphers.affine(values, a, b, decrypt=False)
                self.assertEqual(ciphers.affine(cipher, a, b), values)
        self.assertEqual(ciphers.atbash([0, 28, 11]), [28, 0, 17])
        with self.assertRaises(ValueError):
            ciphers.affine([0], 29, 0)

    def test_vigenere_hand_computed_and_selective_interrupts(self):
        self.assertEqual(ciphers.vigenere([28, 0, 1, 2], [2, 3], decrypt=False), [1, 3, 3, 5])
        # The middle F is copied, the first F is encrypted normally.
        cipher = ciphers.vigenere([0, 0, 1, 2], [2, 3], decrypt=False, skip_positions=[1])
        self.assertEqual(cipher, [2, 0, 4, 4])
        self.assertEqual(ciphers.vigenere(cipher, [2, 3], skip_positions=[1]), [0, 0, 1, 2])
        with self.assertRaises(ValueError):
            ciphers.vigenere([0], [])
        for skips in ([1], [-1], [0, 0], [False]):
            with self.subTest(skips=skips), self.assertRaises(ValueError):
                ciphers.vigenere([0], [1], skip_positions=skips)

    def test_keystream_consumption_and_prime_totients(self):
        stream = count(30)
        self.assertEqual(ciphers.keystream([3, 0, 5], stream, skip_positions=[1]), [2, 0, 3])
        self.assertEqual(next(stream), 32)
        self.assertEqual(list(islice(ciphers.prime_totients(), 8)), [1, 2, 4, 6, 10, 12, 16, 18])
        with self.assertRaises(ValueError):
            ciphers.keystream([1, 2], [1])

    def test_autokey_vectors_both_feedback_modes(self):
        # Seed [4,5], then original plaintext [1,2,...] OR ciphertext [5,7,...].
        plain = [1, 2, 3, 4, 5]
        self.assertEqual(ciphers.autokey(plain, [4, 5], decrypt=False), [5, 7, 4, 6, 8])
        self.assertEqual(ciphers.autokey(plain, [4, 5], decrypt=False, feedback="ciphertext"), [5, 7, 8, 11, 13])
        for feedback in ("plaintext", "ciphertext"):
            for skips in ([], [1, 3]):
                cipher = ciphers.autokey(plain, [4, 5], decrypt=False, feedback=feedback, skip_positions=skips)
                self.assertEqual(ciphers.autokey(cipher, [4, 5], feedback=feedback, skip_positions=skips), plain)

    def test_substitution_bijection(self):
        key = list(reversed(range(29)))
        plain = [0, 2, 2, 28]
        self.assertEqual(ciphers.substitution(ciphers.substitution(plain, key, decrypt=False), key), plain)
        with self.assertRaises(ValueError):
            ciphers.substitution(plain, [0] * 29)


class StatisticsTests(unittest.TestCase):
    def test_uniform_and_degenerate_statistics(self):
        self.assertIsNone(stats.index_of_coincidence([]))
        self.assertIsNone(stats.index_of_coincidence([1]))
        self.assertEqual(stats.entropy([]), 0)
        self.assertEqual(stats.index_of_coincidence([1] * 10), 1)
        self.assertEqual(stats.entropy([1] * 10), 0)
        self.assertAlmostEqual(stats.entropy(range(29)), math.log2(29))
        self.assertEqual(stats.chi_squared(range(29), [1] * 29), 0)

    def test_ngrams_and_periodic_statistics(self):
        values = [1, 2, 1, 2, 1, 2]
        self.assertEqual(stats.ngram_counts(values)[(1, 2)], 3)
        self.assertEqual(stats.repeated_ngrams(values, 3)[(1, 2, 1)], [0, 2])
        lags = stats.lag_coincidences(values, 20)
        self.assertEqual(len(lags), 5)
        self.assertEqual(lags[1], {"lag": 2, "pairs": 4, "matches": 4, "rate": 1.0})
        self.assertEqual(stats.periodic_ic(values, 2)[1]["ic"], 1)
        self.assertIsNone(stats.periodic_ic(values, 7)[-1]["ic"])
        with self.assertRaises(ValueError):
            stats.ngram_counts(values, 0)

    def test_crosspage_alignment(self):
        result = crosspage.aligned_differences([1, 2, 3], [9, 1, 2, 3], shift=1)
        self.assertEqual((result["overlap"], result["equality_rate"]), (3, 1.0))
        self.assertEqual(crosspage.aligned_differences([1], [1], shift=10)["overlap"], 0)
        self.assertIsNone(crosspage.aligned_differences([1], [1], shift=-10)["equality_rate"])
        self.assertEqual(crosspage.shared_ngrams({"a": [1, 2], "b": [2, 3]}, 2), {})

    def test_ngram_training_does_not_cross_documents(self):
        model = NGramModel.train([[1, 2, 3], [1, 2, 4]], order=2)
        self.assertNotIn((3, 1), model.counts)
        self.assertGreater(model.score([1, 2, 3]), model.score([25, 26, 27]))
        self.assertEqual(model.score([1]), float("-inf"))
        with self.assertRaises(ValueError):
            NGramModel.train([[1]], order=2)


class TranspositionAndCribTests(unittest.TestCase):
    def test_known_ragged_columnar_vector_and_inverses(self):
        self.assertEqual(transpositions.columnar(range(8), [2, 0, 1], decrypt=False), [2, 5, 0, 3, 6, 1, 4, 7])
        for size in range(35):
            values = [i % 29 for i in range(size)]
            for order in ([0], [2, 0, 1], [3, 1, 0, 2]):
                self.assertEqual(transpositions.columnar(transpositions.columnar(values, order, decrypt=False), order), values)
            for rails in (2, 3, 8):
                self.assertEqual(transpositions.rail_fence(transpositions.rail_fence(values, rails, decrypt=False), rails), values)

    def test_crib_recovers_key_and_rejects_conflicts(self):
        plain, key = [1, 2, 5, 8, 12, 16], [3, 7]
        cipher = ciphers.vigenere(plain, key, decrypt=False)
        self.assertEqual(known_plaintext.periodic_key_constraints(cipher, plain, 2), tuple(key))
        self.assertEqual(known_plaintext.periodic_key_constraints(cipher, plain[3:], 2, offset=3), tuple(key))
        self.assertEqual(known_plaintext.periodic_key_constraints(cipher, [plain[0]], 2), (3, None))
        self.assertIsNone(known_plaintext.periodic_key_constraints(cipher, plain[:-1] + [0], 2))
        self.assertEqual(known_plaintext.derive_keystream(cipher, plain), key * 3)
        self.assertEqual(known_plaintext.substitution_constraints([1, 2, 1], [3, 4, 3]), {1: 3, 2: 4})
        self.assertIsNone(known_plaintext.substitution_constraints([1, 2], [3, 3]))


class SearchTests(unittest.TestCase):
    def test_annealing_reproducible_budget_and_solution(self):
        objective = lambda s: -sum(abs(a - b) for a, b in zip(s, (0, 1, 2, 3)))
        options = dict(evaluations=200, seed=71)
        a = search.simulated_annealing((3, 2, 1, 0), objective, **options)
        b = search.simulated_annealing((3, 2, 1, 0), objective, **options)
        self.assertEqual(a, b)
        self.assertEqual((a.state, a.evaluations, a.score), ((0, 1, 2, 3), 200, 0))
        self.assertEqual(search.simulated_annealing((1,), sum, evaluations=1, seed=0).evaluations, 1)

    def test_genetic_budget_and_permutation(self):
        objective = lambda s: -sum(abs(a - b) for a, b in zip(s, (0, 1, 2, 3)))
        population = [(3, 2, 1, 0), (2, 3, 0, 1), (1, 0, 3, 2)]
        a = search.genetic_search(population, objective, evaluations=100, seed=5, mutation_rate=1)
        b = search.genetic_search(population, objective, evaluations=100, seed=5, mutation_rate=1)
        self.assertEqual(a, b)
        self.assertEqual(a.evaluations, 100)
        self.assertEqual(sorted(a.state), list(range(4)))
        for _ in range(10):
            self.assertEqual(sorted(search.permutation_crossover(population[0], population[1], Random(_))), list(range(4)))

    def test_beam_constraints_and_hard_bound(self):
        expand = lambda state: (state + (x,) for x in range(3))
        result = search.beam_search((), expand, sum, depth=3, width=5, max_nodes=100,
                                    constraint=lambda s: sum(s) <= 3)
        self.assertEqual(result.completed_depth, 3)
        self.assertEqual(result.candidates[0][1], 3)
        infinite = lambda state: (state + (x,) for x in count())
        bounded = search.beam_search((), infinite, sum, depth=2, width=2, max_nodes=7)
        self.assertEqual(bounded.visited, 7)
        self.assertTrue(bounded.exhausted_budget)

    def test_finite_domain_solver(self):
        result = search.solve_constraints([[0, 1], [0, 1]], lambda p: len(set(p)) == len(p), max_nodes=20, max_solutions=10)
        self.assertTrue(result.complete)
        self.assertEqual(set(result.solutions), {(0, 1), (1, 0)})
        bounded = search.solve_constraints([[0, 1]] * 10, lambda p: True, max_nodes=3, max_solutions=10)
        self.assertEqual(bounded.visited, 3)
        self.assertFalse(bounded.complete)

    def test_invalid_search_parameters(self):
        with self.assertRaises(ValueError):
            search.simulated_annealing((1,), sum, evaluations=0, seed=0)
        with self.assertRaises(ValueError):
            search.simulated_annealing((1,), lambda s: float("nan"), evaluations=2, seed=0)
        with self.assertRaises(ValueError):
            search.genetic_search([(1,)], sum, evaluations=10, seed=0)


if __name__ == "__main__":
    unittest.main()
