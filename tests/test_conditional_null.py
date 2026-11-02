import itertools
from collections import Counter
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from conditional_attack_null import conditional_shuffle,doubles


class ConditionalNullTests(unittest.TestCase):
    def test_exact_labeled_permutation_multiplicities(self):
        values=[0,0,1,1,2]
        accepted=Counter()
        for positions in itertools.permutations(range(len(values))):
            output=tuple(values[i] for i in positions)
            if doubles(output)==1:accepted[output]+=1
        self.assertEqual(len(accepted),12)
        self.assertEqual(set(accepted.values()),{4})

    def test_samples_preserve_counts_and_doubles(self):
        values=[0,0,1,1,2];rng=random.Random(3301009)
        seen=set()
        for _ in range(100):
            sample,proposals=conditional_shuffle(values,rng)
            self.assertEqual(Counter(sample),Counter(values))
            self.assertEqual(doubles(sample),doubles(values))
            self.assertGreater(proposals,0);seen.add(tuple(sample))
        self.assertGreater(len(seen),1)

    def test_proposal_cap_is_not_silently_accepted(self):
        with self.assertRaises(TimeoutError):conditional_shuffle([0,1],random.Random(0),max_proposals=0)
