"""Source-anchored exact controls, independent of statistical language scoring."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from liberprimus.alphabet import to_indices, to_runes
from liberprimus.ciphers import atbash, affine, vigenere, keystream, prime_totients


class KnownSolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=json.loads((ROOT/"transcriptions/pages.json").read_text(encoding="utf-8"))
        cls.fixtures=json.loads((ROOT/"known_solutions/fixtures.json").read_text(encoding="utf-8"))

    def test_all_nine_published_controls_exactly(self):
        self.assertEqual(len(self.fixtures),9)
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["id"]):
                cipher=to_indices(fixture["ciphertext_runes"])
                skips=fixture["skip_positions"]
                method=fixture["cipher"]
                if method=="atbash":
                    plain=atbash(cipher)
                elif method=="vigenere":
                    plain=vigenere(cipher,fixture["key_indices"],skip_positions=skips)
                elif method=="prime_minus_one":
                    plain=keystream(cipher,prime_totients(),skip_positions=skips)
                elif method=="affine_plaintext_formula_2_minus_c":
                    plain=affine(cipher,28,2,decrypt=False)
                elif method=="direct":
                    plain=cipher
                else:
                    self.fail(f"Unknown fixture method {method}")
                self.assertEqual(plain,fixture["expected_indices"])
                self.assertEqual(to_runes(plain),fixture["expected_runes"])

    def test_fixtures_match_canonical_pages(self):
        by_id={p["id"]:p for p in self.pages}
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["id"]):
                text="".join(by_id[page]["runes"] for page in fixture["page_ids"])
                if fixture["id"] == "LP1-06_09_atbash_shift":
                    self.assertFalse(fixture["canonical_pages_match"])
                    self.assertFalse(fixture["eligible_language_training"])
                    self.assertEqual(len(text),778)
                    self.assertEqual(len(fixture["ciphertext_runes"]),780)
                    self.assertEqual(text[:142]+"ᚹᛋ"+text[143:278]+"ᚹᛋ"+text[279:],fixture["ciphertext_runes"])
                else:
                    self.assertTrue(fixture["canonical_pages_match"])
                    self.assertEqual(text,fixture["ciphertext_runes"])

    def test_blanket_f_skip_fails_known_totient_control(self):
        fixture=next(f for f in self.fixtures if f["id"]=="LP2-56_totient_primes")
        cipher=to_indices(fixture["ciphertext_runes"])
        skips=[i for i,c in enumerate(cipher) if c==0]
        self.assertEqual(skips,[35,47,51,56,74])
        self.assertNotEqual(keystream(cipher,prime_totients(),skip_positions=skips),fixture["expected_indices"])

    def test_page_inventory_and_cross_source_agreement(self):
        lp2=[p for p in self.pages if p["edition"]=="LP2"]
        self.assertEqual(sorted(p["page"] for p in lp2),list(range(58)))
        self.assertEqual(len(self.pages),75)
        self.assertEqual(next(p for p in lp2 if p["page"]==50)["runes"],"")
        self.assertEqual(sum(len(p["runes"]) for p in lp2 if p["page"]<=55),12956)
        comparison=json.loads((ROOT/"transcriptions/comparison.json").read_text(encoding="utf-8"))["pages"]
        self.assertEqual(len(comparison),58)
        self.assertTrue(all(row["runes_equal"] for row in comparison))

    def test_manifest_checksums(self):
        manifest=json.loads((ROOT/"sources/manifest.json").read_text(encoding="utf-8"))
        for item in manifest["files"]:
            with self.subTest(source=item["id"]):
                data=(ROOT/item["local_path"]).read_bytes()
                self.assertEqual(len(data),item["bytes"])
                self.assertEqual(hashlib.sha256(data).hexdigest(),item["sha256"])
                self.assertIn(item["commit"],item["url"])


if __name__=="__main__":
    unittest.main()

