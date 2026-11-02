from collections import Counter
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from heldout_language import tokenize,corpus
from external_language import paragraphs
from liberprimus.alphabet import latin_to_indices


class HeldoutTests(unittest.TestCase):
    def test_apostrophe_join_preserves_rune_stream(self):
        split,joined,joins=tokenize("T'H DON'T rock’n’roll; Æsir")
        self.assertEqual(split[:2],[tuple(latin_to_indices('T')),tuple(latin_to_indices('H'))])
        self.assertEqual(joined[0],split[0]+split[1])
        self.assertNotEqual(joined[0],tuple(latin_to_indices('TH')))
        self.assertEqual([s for w in split for s in w],[s for w in joined for s in w])
        self.assertEqual(len(joins),4)

    def test_partition_conserves_original_training_material(self):
        rows=corpus();sequences,counts,_=paragraphs()
        self.assertEqual(Counter(w for r in rows for w in r['words']),counts)
        self.assertEqual([[s for w in r['words'] for s in w] for r in rows],sequences)
        self.assertNotIn('II',{r['chapter'] for r in rows})
        train=[r['source_character_range'] for r in rows if r['chapter'] not in ('X','XI','XII')]
        held=[r['source_character_range'] for r in rows if r['chapter'] in ('X','XI','XII')]
        self.assertTrue(all(b<=c or a>=d for a,b in train for c,d in held))
