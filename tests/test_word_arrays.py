from pathlib import Path
import random
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from liberprimus.decoding import BackoffModel
from liberprimus.word_model import WordModel
from word_arrays import WordArrays


class WordArrayTests(unittest.TestCase):
    def test_exact_mixture_including_leading_zero_and_long_segments(self):
        rng=random.Random(3340);seq=[[rng.randrange(29) for _ in range(80)] for _ in range(4)]
        counts={(0,0):4,(0,1):9,(1,0):2,tuple(range(13)):5}
        model=WordModel(counts,BackoffModel(seq,order=4),tau=20);arrays=WordArrays(model)
        rows=[[0,0,0,1,1,0]+list(range(13))]
        rows += [[rng.randrange(29) for _ in range(19)] for _ in range(8)]
        ends=[2,4,6,19]
        actual=arrays.score(np.array(rows,dtype=np.int32),ends)
        for row,score in zip(rows,actual):self.assertAlmostEqual(score,model.score(row,ends),places=12)

    def test_many_segments_and_word_lengths_without_dictionary_entries(self):
        model=WordModel({(1,):2},BackoffModel([[1,2,3,4,0]*5],order=4))
        rows=np.array([[1,2,3,4,0,1],[0,0,0,0,0,0]],dtype=np.int32);ends=[1,3,4,6]
        got=WordArrays(model).score(rows,ends)
        for row,score in zip(rows.tolist(),got):self.assertAlmostEqual(score,model.score(row,ends),places=12)
