import unittest
from liberprimus.boundaries import parse_layout,segments

class BoundaryTests(unittest.TestCase):
    def test_lines_join_and_punctuation_separates(self):
        parsed=parse_layout('ᚠᚢ/\nᚦ•ᚩ-ᚱ.ᚳ')
        self.assertEqual(parsed['runes'],'ᚠᚢᚦᚩᚱᚳ')
        self.assertEqual(parsed['segment_ends'],[3,4,5,6])
        self.assertEqual(segments(parsed['runes'],parsed['segment_ends']),['ᚠᚢᚦ','ᚩ','ᚱ','ᚳ'])
    def test_alias_and_nonrune_evidence_retained(self):
        parsed=parse_layout('ᛂᚠ\n123abc\nᚢᛜ')
        self.assertEqual(parsed['runes'],'ᛄᚠᚢᛝ')
        self.assertEqual(parsed['segment_ends'],[2,4])
        self.assertEqual(len(parsed['aliases']),2)
        self.assertEqual(len(parsed['nonrune_characters']),6)
        with self.assertRaises(ValueError):parse_layout('ᚠ@ᚢ')
        with self.assertRaises(ValueError):segments([0,1],[2,2])
