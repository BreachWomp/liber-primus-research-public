import itertools
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from joint_skip_search import seed_ranges,optimize_schedule,fixed_schedule_key
from liberprimus.periodic_key import decrypt,encrypt
from liberprimus.decoding import BackoffModel
from ngram_arrays import dense_tables


class JointSkipTests(unittest.TestCase):
    def test_source_runs_stable_order_and_truncation(self):
        cipher=[1]*32+[0]+[2]*300+[0]+[3]*32+[0]+[4]*31
        self.assertEqual(seed_ranges(cipher),[(33,289),(0,32),(334,366)])
        self.assertEqual(seed_ranges([0]*50),[])

    def test_exact_schedule_equals_exhaustive_phase_and_mask(self):
        cipher=[1,0,2,0,0,4,3,0];key=[2,0,8];model=BackoffModel([[1,0,2,4,2,0]*10,[3,2,0,1]*7],order=4)
        for sign in (-1,1):
            best=-float('inf')
            for phase in range(3):
                rotated=key[phase:]+key[:phase]
                for bits in itertools.product((False,True),repeat=4):
                    skips=[i for i,b in zip([1,3,4,7],bits) if b]
                    plain=decrypt(cipher,rotated,sign,skips);best=max(best,model.score(plain))
            found=optimize_schedule(cipher,key,sign,model,time.perf_counter()+5)
            self.assertAlmostEqual(best,found['language_score'],places=12)
            self.assertLessEqual(found['dp_max_states'],24)
            plain=decrypt(cipher,found['key'],sign,found['skip_positions'])
            self.assertEqual(encrypt(plain,found['key'],sign,found['skip_positions']),cipher)
            updated,_=fixed_schedule_key(cipher,found['key'],sign,found['skip_positions'],
                                         dense_tables(model),time.perf_counter()+5)
            self.assertGreaterEqual(model.score(decrypt(cipher,updated,sign,found['skip_positions']))+1e-12,best)
