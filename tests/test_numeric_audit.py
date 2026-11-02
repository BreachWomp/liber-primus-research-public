from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from numeric_source_audit import value,token_rows

class NumericAuditTests(unittest.TestCase):
    def test_case_is_significant_and_standard_vectors(self):
        self.assertEqual([value(x) for x in ['00','0x','10','4F']],[0,59,60,255])
        self.assertNotEqual(value('1L'),value('1l'))
        self.assertNotEqual(value('3I'),value('3i'))
        with self.assertRaises(ValueError):value('0y')

    def test_source_delimiters_without_character_normalization(self):
        cells=['1L','1l','3I','3i','00','4F','0x','2S']
        self.assertEqual(token_rows('-'.join(cells)+'/\nᚠᚢ',hyphens=True),[cells])
        self.assertEqual(token_rows('\t'.join(cells)),[cells])
