from collections import Counter
from pathlib import Path
import sys
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from section_key_support import artificial_spans,page_null
from liberprimus.periodic_key import decrypt,encrypt


class SectionKeyTests(unittest.TestCase):
    def test_page_null_preserves_internal_and_join_statistics(self):
        values=[0,1,2,1,1,3,4,4,0,3,2,2,1,4,4]
        spans=artificial_spans([6,0,9],'test')
        sample,records=page_null(values,spans,71,time.perf_counter()+5)
        doublets=lambda x:sum(a==b for a,b in zip(x,x[1:]))
        for span in spans:
            a,b=span['start'],span['end'];source=values[a:b];shuffled=sample[a:b]
            self.assertEqual(Counter(source),Counter(shuffled))
            self.assertEqual(doublets(source),doublets(shuffled))
            if source:self.assertEqual((source[0],source[-1]),(shuffled[0],shuffled[-1]))
        self.assertEqual(doublets(values),doublets(sample))
        self.assertEqual(records[1]['proposals'],0)

    def test_cursor_continues_across_empty_and_nonempty_pages(self):
        plain=[1,0,2,3,0,7,2,4,0,8];key=[2,3,8];skips=[1,8]
        cipher=encrypt(plain,key,-1,skips);spans=artificial_spans([3,0,4,3],'test')
        self.assertEqual(decrypt(cipher,key,-1,skips),plain)
        cursor=0;recovered=[]
        for span in spans:
            for i in range(span['start'],span['end']):
                if i in skips:recovered.append(0)
                else:recovered.append((-cipher[i]+key[cursor%3])%29);cursor+=1
        self.assertEqual(recovered,plain)
