import unittest
from liberprimus.numeric_statistics import statistics, descriptive

class NumericStatisticsTests(unittest.TestCase):
    def test_extreme_and_balanced_vectors(self):
        zero = statistics(bytes(256))
        self.assertEqual(zero['collision_deviation'], 65025)
        self.assertEqual(zero['adjacent_repeat_deviation'], 65025)
        self.assertEqual(zero['max_bit_imbalance'],256)
        self.assertEqual(zero['column_sum_dispersion'],0)
        once = bytes(range(256))
        self.assertEqual(statistics(once)['max_bit_imbalance'],0)
        self.assertEqual(descriptive(once)['empirical_entropy_bits'],8)
        self.assertEqual(descriptive(once)['distinct_values'],256)
        with self.assertRaises(ValueError): statistics(bytes(255))

    def test_complement_symmetry(self):
        data = bytes((i*i+7*i+19)%256 for i in range(256))
        self.assertEqual(statistics(data), statistics(bytes(255-x for x in data)))
