import random
import unittest
from liberprimus.difference_substitution import differences,integrate,decode,encode


class DifferenceSubstitutionTests(unittest.TestCase):
    def test_literal_first_rune_and_modular_wrap(self):
        self.assertEqual(differences([2,1,1,28],17),[14,28,0,27])
        self.assertEqual(integrate([14,28,0,27],17),[2,1,1,28])
        self.assertEqual(differences([0],0),[0])
        self.assertEqual(integrate([],28),[])

    def test_roundtrip_all_initial_values(self):
        rng=random.Random(3301085)
        for n in (1,2,29,277):
            p=[rng.randrange(29) for _ in range(n)];key=list(range(29));rng.shuffle(key)
            for iv in range(29):
                c=encode(p,key,iv)
                self.assertEqual(len(c),n)
                self.assertEqual(decode(c,key,iv),p)
                self.assertEqual(integrate(differences(c,iv),iv),c)

    def test_reject_nonpermutations_and_invalid_iv(self):
        for key in ([0]*29,list(range(28))):
            with self.assertRaises(ValueError):decode([1],key)
        for iv in (-1,29,True):
            with self.assertRaises(ValueError):differences([1],iv)
