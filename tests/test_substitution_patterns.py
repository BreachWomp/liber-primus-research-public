from collections import Counter
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from liberprimus.substitution_patterns import equality_pattern,complete_mapping
from liberprimus.known_plaintext import substitution_constraints


class SubstitutionPatternTests(unittest.TestCase):
    def test_repeated_symbol_bijection_constraint(self):
        a=[7,4,7,2,4];b=[0,28,0,3,28]
        self.assertEqual(equality_pattern(a),(0,1,0,2,1))
        self.assertEqual(equality_pattern(a),equality_pattern(b))
        self.assertEqual(substitution_constraints(a,b),{7:0,4:28,2:3})
        self.assertIsNone(substitution_constraints(a,[0,28,3,3,28]))

    def test_completion_preserves_partial_bijection_and_frequency_order(self):
        mapping=complete_mapping({7:0,4:28},Counter({2:20,3:5}),Counter({9:30,10:4}))
        self.assertEqual(sorted(mapping),list(range(29)))
        self.assertEqual([mapping[i] for i in [7,4,2,3]],[0,28,9,10])
        with self.assertRaises(ValueError):complete_mapping({1:4,2:4},{},{})
