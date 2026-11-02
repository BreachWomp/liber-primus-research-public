import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("adjacency", Path(__file__).resolve().parents[1] / "experiments/adjacency.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AdjacencyTests(unittest.TestCase):
    def test_holm_monotonicity_and_order(self):
        self.assertEqual(MODULE.holm([0.02, 0.001, 0.8]), [0.04, 0.003, 0.8])

    def test_boundaries_are_not_silently_concatenated(self):
        values, masks = MODULE.page_arrays({"id": "test", "runes": "ᚠᚠᚠᚠ", "text_with_layout": "ᚠᚠ•ᚠ\nᚠ"})
        self.assertEqual(values.tolist(), [0, 0, 0, 0])
        self.assertEqual(masks["stream"].tolist(), [True, True, True])
        self.assertEqual(masks["within_word"].tolist(), [True, False, False])
        self.assertEqual(masks["within_line"].tolist(), [True, True, False])

    def test_layout_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.page_arrays({"id": "bad", "runes": "ᚠ", "text_with_layout": "ᚢ"})

    def test_plus_one_and_ties(self):
        result = MODULE.describe(0, MODULE.np.array([0, 1, 2]), 1.0, 3)
        self.assertEqual(result["p_lower"], 0.5)


if __name__ == "__main__":
    unittest.main()
