import importlib.util
from pathlib import Path
import unittest

SPEC=importlib.util.spec_from_file_location("period_scan",Path(__file__).resolve().parents[1]/"experiments/period_scan.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
from liberprimus.stats import periodic_ic


class PeriodScanTests(unittest.TestCase):
    def test_vectorized_ragged_ic_matches_scalar(self):
        rows=MODULE.np.array([[0,1,2,0,1,2,0],[1,1,1,2,2,2,2]],dtype=MODULE.np.int16)
        for period in range(1,8):
            scores,pairs=MODULE.periodic_rows(rows,period)
            for row,score in zip(rows,scores):
                expected=periodic_ic(row.tolist(),max_period=period)[-1]
                self.assertEqual(pairs,expected["ordered_pairs"])
                if pairs:self.assertAlmostEqual(score,expected["ic"])
                else:self.assertTrue(MODULE.np.isnan(score))


if __name__=="__main__":unittest.main()
