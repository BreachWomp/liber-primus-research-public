"""Source-preserving long-stream controls before any unknown section scan."""
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,digest
from periodic_key_controls import models
from joint_skip_external import DEPS as JOINT_DEPS
from section_key_support import join_pages,artificial_spans,page_null
from long_key_search import search
from liberprimus.periodic_key import encrypt,decrypt
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/long_key_plan.json'
SOURCE='results/E043-section-key-controls-73aef4cf11c1.json'


def run():
    tick=time.perf_counter();deadline=tick+180;model,_,training=models();lookup=dense_tables(model)
    rng=random.Random(3301049);controls=[]
    for j,source in enumerate(load(SOURCE)['controls']):
        plain=to_indices(source['truth_runes']);key=[rng.randrange(1,29) for _ in range((17,23,31)[j])]
        sign=(1,-1,1)[j];skips=[i for i,x in enumerate(plain) if x==0][::2]
        cipher=encrypt(plain,key,sign,skips);result=search(cipher,model,lookup,deadline);top=result['top'][0]
        checks={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
                'key_exact':top['key']==key and top['sign']==sign,'mask_exact':top['skip_positions']==skips}
        controls.append({'chapter':source['chapter'],'source_ranges':source['source_ranges'],
            'truth_runes':source['truth_runes'],'page_spans':source['page_spans'],'injected_key':key,
            'injected_sign':sign,'injected_skips':skips,'ciphertext_indices':cipher,'result':result,
            'checks':checks,'exact':all(checks.values())})
        print({'chapter':source['chapter'],'checks':checks,'seconds':time.perf_counter()-tick},flush=True)
    source=controls[1];sample,proposals=page_null(source['ciphertext_indices'],source['page_spans'],3302049,deadline)
    null={'control_index':1,'page_spans':source['page_spans'],'ciphertext_indices':sample,
          'page_proposals':proposals,'result':search(sample,model,lookup,deadline)}
    return {'experiment':'E049-long-key-controls','parameters':load(PLAN),'training':training,
            'controls':controls,'nulls':[null],'gate_passed':all(r['exact'] for r in controls),
            'unknown_sections_searched':0,'new_decryptions':[],'wall_seconds':time.perf_counter()-tick}


DEPS=JOINT_DEPS+[PLAN,SOURCE,'experiments/long_key_search.py','experiments/long_key_controls.py',
                'experiments/section_key_support.py','transcriptions/pages.json']
if __name__=='__main__':registered('E049-long-key-controls',load(PLAN)|{'numpy':np.__version__},DEPS,run)
