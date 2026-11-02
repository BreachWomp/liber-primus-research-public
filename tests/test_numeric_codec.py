import copy
import unittest
from liberprimus.numeric import apply_overlay, decode_pair, encode_pair

class NumericCodecTests(unittest.TestCase):
    def test_full_domain_and_case(self):
        for n in range(3600):
            self.assertEqual(decode_pair(encode_pair(n)), n)
        self.assertEqual([decode_pair(s) for s in ['0I','0L','0i','0l','2S','2s']], [18,21,44,47,148,174])
        for token in ['I','00I','0y',' 0']:
            with self.assertRaises(ValueError): decode_pair(token)
        for n in [-1,3600,1.5,True]:
            with self.assertRaises(ValueError): encode_pair(n)

    def test_overlay_preserves_source_and_checks_base(self):
        pages = [{'page_id':'LP2-49','tokens_by_source':{'relikd_canonical':[['1L']]}}]
        original = copy.deepcopy(pages)
        item = {'page_id':'LP2-49','row_1based':1,'column_1based':1,
                'historical_alternatives':['1L','1l'],'selected_token':'1l'}
        self.assertEqual(apply_overlay(pages,[item]), {'LP2-49':[['1l']]})
        self.assertEqual(pages, original)
        with self.assertRaises(ValueError): apply_overlay(pages,[item,item])
        item['historical_alternatives']=['1l']
        with self.assertRaises(ValueError): apply_overlay(pages,[item])
