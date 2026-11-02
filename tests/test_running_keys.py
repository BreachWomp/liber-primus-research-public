from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from running_key_attack import source_keys,scan,SIGNS
from ciphertext_autokey_scan import tables
from liberprimus.decoding import BackoffModel,replay


class RunningKeyTests(unittest.TestCase):
    def test_vector_search_matches_exhaustive_scalar_search(self):
        values=[1,0,4,5,0,2];key=[2,1,4,6,0,7,2,11,3]
        model=BackoffModel([[1,2,3,0,4,5,1,2,0,6,4,3]])
        best=-float("inf");count=0
        for skip in (False,True):
            skips=[i for i,v in enumerate(values) if skip and v==0]
            for cs,ks in SIGNS:
                for start in range(len(key)-len(values)+len(skips)+1):
                    out=replay(values,key,repeating=False,start=start,skip_positions=skips,cipher_sign=cs,key_sign=ks)
                    best=max(best,model.score(out));count+=1
        actual,_,tasks=scan(values,{"toy":key},tables(model),time.perf_counter()+10,batch=2)
        self.assertAlmostEqual(actual,best,places=12);self.assertEqual(tasks,count)

    def test_pinned_chapter_and_explicit_encodings(self):
        keys,meta=source_keys()
        self.assertEqual(set(keys),{"Q_to_C","QU_to_CW_Q_to_C"})
        self.assertNotEqual(keys["Q_to_C"],keys["QU_to_CW_Q_to_C"])
        self.assertTrue(all(10000<len(k)<100000 for k in keys.values()))
        self.assertGreater(meta["decoded_character_range"][1],meta["decoded_character_range"][0])
