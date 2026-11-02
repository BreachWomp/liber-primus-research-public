from itertools import combinations
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from long_key_search import source_windows
from joint_skip_search import optimize_schedule
from liberprimus.periodic_key import decrypt
from liberprimus.decoding import BackoffModel


class LongKeyTests(unittest.TestCase):
    def test_sources_rank_full_runs_before_capping(self):
        values=[1]*70+[0]+[2]*520+[0]+[3]*80+[0]+[4]*63
        sources=source_windows(values)
        self.assertEqual(sources[0],('whole',0,len(values),None))
        self.assertEqual(sources[1:],[('non_F_run',71,583,[]),('non_F_run',592,672,[]),('non_F_run',0,70,[])])

    def test_32_slot_schedule_matches_phase_mask_enumeration(self):
        model=BackoffModel([[1,2,0,3,4]*6],order=4)
        values=[0,2,4,0,1];key=[(i*7+3)%29 for i in range(32)];fs=[0,3];best=-float('inf')
        for phase in range(32):
            oriented=key[phase:]+key[:phase]
            for n in range(3):
                for skips in combinations(fs,n):best=max(best,model.score(decrypt(values,oriented,-1,skips)))
        result=optimize_schedule(values,key,-1,model,time.perf_counter()+5)
        self.assertAlmostEqual(best,result['language_score'],places=12)
        self.assertLessEqual(result['dp_max_states'],256)
