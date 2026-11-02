from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from section_stream_attack import assemble
from attack_support import load,to_indices
from liberprimus.decoding import replay
from liberprimus.ciphers import keystream


class SectionTests(unittest.TestCase):
    def test_numeric_page_is_present_at_zero_width(self):
        section=next(s for s in load("experiments/section_plan.json")["sections"] if s["id"]=="LP2-40_55")
        values,spans=assemble(section)
        numeric=next(p for p in spans if p["page"]=="LP2-50")
        self.assertEqual(numeric["start"],numeric["end"])
        self.assertTrue(numeric["layout"].strip())
        self.assertEqual(spans[-1]["end"],len(values))
        self.assertEqual([s["page"] for s in spans],section["page_ids"])

    def test_split_recipe_advances_by_active_runes_only(self):
        plain=[1,2,0,4,5,6,0,8,9];key=list(range(40));start=3;skips=[2,6]
        cipher=keystream(plain,key[start:],decrypt=False,skip_positions=skips)
        first=replay(cipher[:5],key,repeating=False,start=start,skip_positions=[2])
        second=replay(cipher[5:],key,repeating=False,start=start+4,skip_positions=[1])
        self.assertEqual(first+second,plain)
        self.assertNotEqual(replay(cipher[5:],key,repeating=False,start=start,skip_positions=[1]),plain[5:])
