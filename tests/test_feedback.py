import unittest
from liberprimus.feedback import basis,decrypt,encrypt

class FeedbackTests(unittest.TestCase):
    def test_basis_matches_independent_recurrence(self):
        cipher=[(i*i+3*i+7)%29 for i in range(35)]
        for delay in [1,2,3]:
            for a,b in [(1,28),(5,11),(28,3)]:
                seed=list(range(delay));plain=decrypt(cipher,a,b,seed)
                self.assertEqual(encrypt(plain,a,b,seed),cipher)
                base,powers=basis(cipher,b,delay)
                expanded=[(a*s+q*plain[i%delay])%29 for i,(s,q) in enumerate(zip(base,powers))]
                self.assertEqual(expanded,plain)
                recovered=[(plain[r]-a*cipher[r])*pow(b,-1,29)%29 for r in range(delay)]
                self.assertEqual(recovered,seed)

    def test_hand_example(self):
        self.assertEqual(decrypt([1,2,3,4],2,3,[4,5]),[14,19,19,7])
        self.assertEqual(encrypt([14,19,19,7],2,3,[4,5]),[1,2,3,4])
