"""E072: registered blind-key affine-constant controls."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices
from periodic_key_controls import models
from bilinear_feedback_controls import control_source as old_source,DEPS as OLD_DEPS
from liberprimus.affine_feedback import encrypt
from affine_feedback_search import search
from ngram_arrays import dense_tables
from registry import registered
PLAN='experiments/delayed_affine_feedback_plan.json'


def control_source(rows,index):
    old_index=index if index<12 else (0,3,6,11)[index-12]
    source=old_source(rows,old_index)
    if index>=12:
        return source|{'constant':0,'reused_input_control':f'E068-control-{old_index}'}
    a=(2,7,14,27)[index%4];b=(1,3,15)[index%3];c=(5*index+1)%28+1
    rng=random.Random(3301072+index);key=[rng.randrange(29) for _ in source['injected_key']]
    source.update(injected_key=key,cipher_sign=a,feedback_sign=b,constant=c,
        ciphertext_indices=encrypt(to_indices(source['truth_runes']),key,a,b,c))
    return source


def run(kind,index):
    tick=time.perf_counter();deadline=tick+180
    model,rows,training=models();source=control_source(rows,index)
    if kind=='null':
        original=source['ciphertext_indices'];rng=random.Random(3302072)
        equal=lambda x:sum(a==b for a,b in zip(x,x[1:]))
        for proposals in range(1,100001):
            if time.perf_counter()>deadline:raise TimeoutError('Null deadline')
            middle=original[1:-1];rng.shuffle(middle);sample=original[:1]+middle+original[-1:]
            if equal(sample)==equal(original):break
        else:raise RuntimeError('Null rejection cap')
        source={'ciphertext_indices':sample,'proposals':proposals,'source_control':5}
    probe=None if kind=='null' else [len(source['injected_key']),source['cipher_sign'],source['feedback_sign'],source['constant']]
    result=search(source['ciphertext_indices'],dense_tables(model),deadline,probe)
    out={'experiment':f'E072-{kind}-{index}','kind':kind,'index':index,'parameters':load(PLAN),
        'training':training,'source':source,'result':result,'new_decryptions':[]}
    if kind=='control':
        top=result['top'][0];r=top['recipe']
        out['exact']=top['plaintext_runes']==source['truth_runes']
        out['injected_recipe_exact']=all(r[k]==source[s] for k,s in [('key_indices','injected_key'),('cipher_sign','cipher_sign'),('feedback_sign','feedback_sign'),('constant','constant')])
        probe=next(r['probe'] for r in result['screen_audit'] if 'probe' in r)
        out['injected_family_rank']=probe['rank'];out['injected_family_retained']=probe['rank']<=8
        out['correct_runes']=sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
    out['wall_seconds']=time.perf_counter()-tick
    print({k:out[k] for k in ('experiment','exact','injected_family_rank','correct_runes','wall_seconds') if k in out},flush=True)
    return out


DEPS=OLD_DEPS+[PLAN,'experiments/phase26_provenance.py','experiments/affine_feedback_controls.py','experiments/affine_feedback_search.py',
    'experiments/affine_feedback_factors.py','src/liberprimus/affine_feedback.py',
    'scripts/run_affine_feedback_controls.py','results/E071-algebra-c88504248ab7.json']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['control','null']);p.add_argument('index',type=int);args=p.parse_args()
    assert 0<=args.index<16 and (args.kind!='null' or args.index==5)
    assert load('results/E071-algebra-c88504248ab7.json')['gate_passed']
    registered(f'E072-{args.kind}-{args.index}',load(PLAN)|vars(args)|{'numpy':np.__version__},DEPS,lambda:run(args.kind,args.index))
