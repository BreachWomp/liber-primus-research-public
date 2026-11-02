"""Adaptive ciphertext-only repair on a failed control, with matched null."""
import time
import numpy as np
from attack_support import load
from long_key_controls import DEPS as CONTROL_DEPS
from phase_key_controls import DEPS as PHASE_DEPS
from periodic_key_controls import models
from section_key_support import page_null
from pooled_long_key_search import search
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/pooled_long_key_plan.json'

def run():
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    source=next(r for r in load(plan['control_output'])['controls'] if r['chapter']=='XII');assert not source['exact']
    model,_,training=models();lookup=dense_tables(model);cipher=source['ciphertext_indices']
    result=search(cipher,model,lookup,deadline,seed=plan['search_seed']);top=result['top'][0]
    checks={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
        'key_exact':top['key']==source['injected_key'] and top['sign']==source['injected_sign'],
        'mask_exact':top['skip_positions']==source['injected_skips']}
    print({'repair_checks':checks,'seconds':time.perf_counter()-tick},flush=True)
    sample,proposals=page_null(cipher,source['page_spans'],3302051,deadline)
    null={'ciphertext_indices':sample,'page_spans':source['page_spans'],'page_proposals':proposals,
        'result':search(sample,model,lookup,deadline,seed=plan['search_seed'])}
    return {'experiment':'E051-pooled-long-key-diagnostic','parameters':plan,'training':training,
        'chapter':'XII','ciphertext_indices':cipher,'page_spans':source['page_spans'],'result':result,
        'checks':checks,'exact':all(checks.values()),'null':null,'adaptive_control_probe':True,
        'gate_for_unknown':False,'unknown_sections_searched':0,'new_decryptions':[],'wall_seconds':time.perf_counter()-tick}

if __name__=='__main__':
    p=load(PLAN);registered('E051-pooled-long-key-diagnostic',p|{'numpy':np.__version__},
        CONTROL_DEPS+PHASE_DEPS+[PLAN,p['control_output'],p['diagnostic_output'],
        'experiments/pooled_long_key_search.py','experiments/pooled_long_key_diagnostic.py'],run)
