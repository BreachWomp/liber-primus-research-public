import itertools
import math
import unittest
from liberprimus.decoding import BackoffModel
from liberprimus.word_model import WordModel
from liberprimus.fragment_model import fragment_score,clip_edges


class FragmentTests(unittest.TestCase):
    def setUp(self):
        self.model=WordModel({(0,1):7,(1,):2},BackoffModel([[0,1,1,0]],order=2))

    def test_normalization_fixed_edges(self):
        # Every length-3 string for edge/interior/edge segmentation.
        total=sum(math.exp(3*fragment_score(self.model,x,[1,2,3],edge_backoff=True))
                  for x in itertools.product(range(29),repeat=3))
        self.assertAlmostEqual(total,1,places=10)

    def test_edge_and_interior_accounting(self):
        values=[0,1,1,0,1];ends=[2,3,5]
        self.assertAlmostEqual(fragment_score(self.model,values,ends),self.model.score(values,ends))
        expected=(4*self.model.character_model.score([0,1])+self.model.logword((1,)))/5
        self.assertAlmostEqual(fragment_score(self.model,values,ends,edge_backoff=True),expected)
        self.assertAlmostEqual(fragment_score(self.model,[0,1],[2],edge_backoff=True),
                               self.model.character_model.score([0,1]))

    def test_clipping_preserves_internal_boundaries(self):
        self.assertEqual(clip_edges([0,1,2,3,4,5,6],[3,4,7],2,1),([2,3,4,5],[1,2,4]))
        for left,right in [(0,1),(3,1),(1,3)]:
            with self.assertRaises(ValueError):clip_edges(list(range(7)),[3,4,7],left,right)
