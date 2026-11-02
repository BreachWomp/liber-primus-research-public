from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from external_language import paragraphs
from running_key_attack import source_keys


class ExternalLanguageTests(unittest.TestCase):
    def test_training_excludes_tested_running_key_chapter(self):
        sequences,counts,meta=paragraphs();_,keymeta=source_keys()
        a,b=keymeta["decoded_character_range"]
        self.assertEqual(len(meta["sections"]),11)
        for section in meta["sections"]:
            c,d=section["source_character_range"]
            self.assertTrue(d<=a or c>=b)
            self.assertNotEqual(section["roman"],"II")
        self.assertGreater(sum(map(len,sequences)),200000)
        self.assertGreater(len(counts),1000)
