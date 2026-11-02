import math
from pathlib import Path
import random
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.periodic_key import primitive,schedule,encrypt,decrypt
from liberprimus.decoding import BackoffModel
from ngram_arrays import dense_tables
from periodic_key_search import factors_at,coordinate


class PeriodicKeyTests(unittest.TestCase):
    def test_reversible_copied_f_and_primitive_key(self):
        values=[0,8,2,0,0,6,4,0];skips=[0,4];key=[3,7,3,7]
        for sign in (-1,1):
            cipher=encrypt(values,key,sign,skips)
            self.assertEqual(decrypt(cipher,key,sign,skips),values)
            self.assertEqual(decrypt(cipher,primitive(key),sign,skips),values)
        self.assertEqual(primitive(key),[3,7])
        self.assertEqual(schedule(values,2,skips),[-1,0,1,0,-1,1,0,1])
        with self.assertRaises(ValueError):schedule(values,2,[1])
        with self.assertRaises(ValueError):primitive([])

    def test_local_update_equals_all_full_candidate_scores(self):
        rng=random.Random(56);values=[rng.randrange(29) for _ in range(50)];values[12]=values[31]=0
        model=BackoffModel([[rng.randrange(29) for _ in range(70)] for _ in range(3)],order=4)
        tables=dense_tables(model);key=[2,9,17,20,6];sign=-1;skips=[12,31]
        slots=np.array(schedule(values,len(key),skips));plain=np.array(decrypt(values,key,sign,skips))
        signed=-np.array(values)
        for lookup in (tables[:2],tables):
            scalar=BackoffModel([[1]],order=len(lookup))
            # Compare exact factor values directly with full conditional sums.
            factors=factors_at(plain[None,:],np.arange(len(plain)),lookup)[0]
            for slot in range(len(key)):
                candidates=[]
                for replacement in range(29):
                    trial=key[:];trial[slot]=replacement;p=decrypt(values,trial,sign,skips)
                    total=sum(float(lookup[min(i,len(lookup)-1)][tuple(p[max(0,i-len(lookup)+1):i+1])]) for i in range(len(p)))
                    candidates.append(total)
                newkey=key[:]
                found,updated,moved=coordinate(plain,signed,np.flatnonzero(slots==slot),slot,newkey,lookup,factors)
                expected=max(candidates)
                self.assertAlmostEqual(float(updated.sum()),expected,places=10)
                self.assertEqual(found.tolist(),decrypt(values,newkey,sign,skips))
        self.assertAlmostEqual(float(factors_at(plain[None,:],np.arange(len(plain)),tables).sum())/len(plain),
                               model.score(plain.tolist()),places=12)
