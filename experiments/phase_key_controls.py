"""Fresh page-phase controls anchored to preserved E043 source spans."""
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from periodic_key_controls import models
from reset_key_controls import DEPS as SECTION_DEPS
from section_key_support import page_null
from phase_key_search import search
from liberprimus.periodic_key import encrypt
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/phase_key_plan.json'
SOURCE='results/E043-section-key-controls-73aef4cf11c1.json'

def run():
    tick=time.perf_counter();deadline=tick+180;model,_,training=models();lookup=dense_tables(model)
    rng=random.Random(3301047);controls=[]
    for j,source in enumerate(load(SOURCE)['controls']):
        plain=to_indices(source['truth_runes']);spans=source['page_spans']
        key=[rng.randrange(1,29) for _ in range((5,8,13)[j])];sign=(1,-1,1)[j]
        skips=[i for i,x in enumerate(plain) if x==0][::2];cipher=[]
        phases=[];first=True
        for span in spans:
            a,b=span['start'],span['end']
            phase=0 if a==b or first else rng.randrange(len(key));phases.append(phase)
            if a!=b:first=False
            cipher+=encrypt(plain[a:b],key[phase:]+key[:phase],sign,[i-a for i in skips if a<=i<b])
        result=search(cipher,spans,model,lookup,deadline);top=result['top'][0]
        checks={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
            'key_exact':top['key']==key and top['sign']==sign,'mask_exact':top['skip_positions']==skips,'phases_exact':top['page_phases']==phases}
        controls.append({'chapter':source['chapter'],'source_ranges':source['source_ranges'],
            'truth_runes':source['truth_runes'],'page_spans':spans,'injected_key':key,'injected_sign':sign,
            'injected_skips':skips,'injected_phases':phases,'ciphertext_indices':cipher,'result':result,'checks':checks,'exact':all(checks.values())})
        print({'chapter':source['chapter'],'checks':checks,'seconds':time.perf_counter()-tick},flush=True)
    source=controls[1];sample,proposals=page_null(source['ciphertext_indices'],source['page_spans'],3302047,deadline)
    null={'control_index':1,'page_spans':source['page_spans'],'ciphertext_indices':sample,
        'page_proposals':proposals,'result':search(sample,source['page_spans'],model,lookup,deadline)}
    return {'experiment':'E047-page-phase-controls','parameters':load(PLAN),'training':training,
        'controls':controls,'nulls':[null],'gate_passed':all(r['exact'] for r in controls),
        'wall_seconds':time.perf_counter()-tick,'unknown_sections_searched':0,'new_decryptions':[]}

DEPS=SECTION_DEPS+[PLAN,SOURCE,'experiments/phase_key_search.py','experiments/phase_key_controls.py']
if __name__=='__main__':registered('E047-page-phase-controls',load(PLAN)|{'numpy':np.__version__},DEPS,run)
