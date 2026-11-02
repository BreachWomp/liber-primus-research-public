import itertools
import math
import unittest
from liberprimus.terminated_words import TerminatedWords,BOS,EOS,TARGETS


class TerminatedWordTests(unittest.TestCase):
    def test_events_normalization_and_eos(self):
        m=TerminatedWords([[1,2],[1,2],[2]])
        self.assertEqual(dict(m.events[()]),{1:2,2:3,EOS:3})
        self.assertEqual(dict(m.events[(BOS,BOS,BOS)]),{1:2,2:1})
        self.assertEqual(dict(m.events[(BOS,1,2)]),{EOS:2})
        for h in ((),(7,),(BOS,BOS,BOS),(BOS,1,2),(8,9,10)):
            self.assertAlmostEqual(sum(math.exp(m.logp(h,s)) for s in TARGETS),1.,places=12)
        expected=m.logp((BOS,)*3,1)+m.logp((BOS,BOS,1),2)+m.logp((BOS,1,2),EOS)
        self.assertAlmostEqual(m.logq([1,2]),expected)
        with self.assertRaises(ValueError):m.logp((),BOS)

    def test_scalar_vector_scores_and_empty_rejection(self):
        try:
            import numpy as np
            from terminated_word_arrays import TerminatedArrays
        except ImportError:self.skipTest('Optional NumPy runner unavailable')
        m=TerminatedWords([[1,2],[1,2],[2],[4,5,6],list(range(15))]);a=TerminatedArrays(m)
        rows=np.array(list(itertools.product((1,2,7),repeat=4)))
        for ends in ([4],[1,4],[2,4],[1,2,3,4]):
            scores=a.score(rows,ends)
            for row,score in zip(rows.tolist(),scores):self.assertAlmostEqual(m.score(row,ends),score,places=12)
        long=np.array([list(range(15)),[28]*15])
        for row,score in zip(long.tolist(),a.score(long,[15])):self.assertAlmostEqual(m.score(row,[15]),score,places=12)
        with self.assertRaises(ValueError):TerminatedWords([[]])
        with self.assertRaises(ValueError):m.score([],[])
