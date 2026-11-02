"""Actual historical controls, never injecting their keys or skip masks."""
import random
import time
import numpy as np
from attack_support import load,to_indices,cycle_key
from periodic_key_controls import models,DEPS as MODEL_DEPS
from joint_skip_search import search
from ngram_arrays import dense_tables
from conditional_attack_null import conditional_shuffle
from registry import registered

PLAN='experiments/joint_skip_plan.json'


def run():
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    model,_,training=models();lookup=dense_tables(model)
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};controls=[]
    for j,ident in enumerate(plan['controls']):
        fixture=fixtures[ident];cipher=to_indices(fixture['ciphertext_runes'])
        result=search(cipher,model,lookup,deadline)
        top=result['top'][0];expected_key=cycle_key([(-x)%29 for x in fixture['key_indices']])
        checks={'plaintext_exact':top['plaintext_runes']==fixture['plaintext_runes'],
                'key_exact':tuple(cycle_key(top['key']))==expected_key and top['sign']==1,
                'mask_exact':top['skip_positions']==fixture['skip_positions']}
        controls.append({'fixture':ident,'ciphertext_indices':cipher,'result':result,'checks':checks,
                         'exact':all(checks.values())})
        print({'control':ident,'checks':checks,'seconds':time.perf_counter()-tick},flush=True)
    nulls=[]
    for j,ctrl in enumerate(controls):
        sample,proposals=conditional_shuffle(ctrl['ciphertext_indices'],random.Random(3302040+j),deadline=deadline)
        result=search(sample,model,lookup,deadline)
        nulls.append({'control_index':j,'ciphertext_indices':sample,'proposals':proposals,'result':result})
        print({'null':j,'seconds':time.perf_counter()-tick},flush=True)
    return {'experiment':'E040-joint-key-skip-controls','parameters':plan,'training':training,
            'controls':controls,'nulls':nulls,'gate_passed':all(r['exact'] for r in controls),
            'unknown_pages_searched':0,'new_decryptions':[],'wall_seconds':time.perf_counter()-tick}


DEPS=MODEL_DEPS+[PLAN,'experiments/joint_skip_controls.py','experiments/joint_skip_search.py']
if __name__=='__main__':registered('E040-joint-key-skip-controls',load(PLAN)|{'numpy':np.__version__},DEPS,run)
