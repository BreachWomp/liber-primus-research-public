from itertools import product
from pathlib import Path
import random
import sys
import time
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from liberprimus.fragment_constraints import build_chains, feasible, maximize, seed_phases


class FragmentConstraintTests(unittest.TestCase):
    def test_optimum_matches_exhaustive_with_wrap_and_multiple_pages(self):
        values = [1,2,0,3,4,0,0,5,6,7,8]
        chains = build_chains(values, [{'start':0,'end':9},{'start':9,'end':11}],
                              [(7,9),(0,2),(3,5),(9,11)])
        rng = random.Random(58)
        for period in (1,2,3,5):
            costs = [[rng.random() for _ in range(period)] for _ in range(4)]
            score, phases = maximize(costs, chains, time.perf_counter()+5)
            expected = -float('inf')
            for p in product(range(period), repeat=4):
                # Independent direct equations, including source-order permutation.
                if not any((p[2]-p[1]-3+s)%period==0 for s in range(2)): continue
                if not any((p[0]-p[2]-4+s)%period==0 for s in range(3)): continue
                expected=max(expected,sum(costs[i][q] for i,q in enumerate(p)))
            self.assertAlmostEqual(score,expected,places=12)
            self.assertTrue(feasible(phases,chains,period))

    def test_gap_with_at_least_one_period_of_choices_is_unconstrained(self):
        values=[1]+[0]*7+[2]
        chains=build_chains(values,[{'start':0,'end':9}],[(0,1),(8,9)])
        costs=[[0.,2.,1.],[3.,0.,1.]]
        score,phases=maximize(costs,chains,time.perf_counter()+5)
        self.assertEqual(score,5.);self.assertEqual(phases,[1,0])

    def test_initializations_are_feasible_and_rotation_invariant(self):
        chains=build_chains([1,0,2,3,0,4],[{'start':0,'end':6}],[(2,4),(0,1),(5,6)])
        for start in range(64):
            phases=seed_phases(chains,7,start,random.Random(start))
            self.assertTrue(feasible(phases,chains,7))
            self.assertTrue(feasible([(p+3)%7 for p in phases],chains,7))

    def test_rejects_cross_page_or_nonfree_fragments_and_deadline(self):
        for ranges in ([(0,3)],[(0,2)]):
            with self.assertRaises(ValueError):
                build_chains([1,0,2],[{'start':0,'end':2},{'start':2,'end':3}],ranges)
        chains=build_chains([1],[{'start':0,'end':1}],[(0,1)])
        with self.assertRaises(TimeoutError):maximize([[1.]],chains,time.perf_counter()-1)
