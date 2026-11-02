from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from liberprimus.layout import rune_rows,row_permutations,permute,scatter

class LayoutRouteTests(unittest.TestCase):
    def test_explicit_ragged_orders_and_inverse(self):
        rows={r['name']:r['indices'] for r in row_permutations([3,2,4])}
        self.assertEqual(len(rows),8)
        self.assertEqual(rows['top_snake_left'],[0,1,2,4,3,5,6,7,8])
        self.assertEqual(rows['bottom_left'],[5,6,7,8,3,4,0,1,2])
        for order in rows.values():
            x=list(range(9));self.assertEqual(scatter(permute(x,order),order),x)
            self.assertEqual(permute(scatter(x,order),order),x)
        with self.assertRaises(ValueError):permute([1,2],[0,0])

    def test_nonrune_rows_do_not_become_padding(self):
        self.assertEqual(rune_rows('ᚠ•ᚢ\n3N\t2a\n\nᚦ⁜'),['ᚠᚢ','ᚦ'])
        with self.assertRaises(ValueError):rune_rows('ᚠᛂ')
        self.assertEqual(len(row_permutations([3])),2)
