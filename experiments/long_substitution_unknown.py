import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices
from long_substitution_controls import DEPS as CONTROL_DEPS
from terminated_benchmark import models
from terminated_search import SearchArrays,solve
from registry import registered
PLAN='experiments/long_substitution_unknown_plan.json'


def run(mode,page,replicate):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    item=next(p for p in plan['pages'] if p['page']==page)
    source=next(p for p in load('transcriptions/pages.json') if p['id']==page)
    cipher=to_indices(source['runes']);proposals=None
    if mode=='null':
        assert page==load('experiments/long_substitution_selection.json')['page']
        rng=random.Random(plan['null_seed']+100*replicate)
        target=sum(a==b for a,b in zip(cipher,cipher[1:]));original=cipher[:]
        for proposals in range(1,100001):
            if time.perf_counter()>deadline:raise TimeoutError('E084 null deadline')
            middle=original[1:-1];rng.shuffle(middle);cipher=original[:1]+middle+original[-1:]
            if sum(a==b for a,b in zip(cipher,cipher[1:]))==target:break
        else:raise TimeoutError('Null proposal cap')
    model,_,old,_,training=models();arrays=SearchArrays(model,old)
    result=solve(cipher,item['segment_ends'],model,arrays,3303084+100*item['number'],deadline)
    return {'experiment':'E084','mode':mode,'page':page,'replicate':replicate,'parameters':plan,
        'ciphertext_indices':cipher,'segment_ends':item['segment_ends'],'null_proposals':proposals,
        'training':training,'result':result,'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['page','null']);p.add_argument('page');p.add_argument('replicate',type=int);a=p.parse_args()
    plan=load(PLAN);assert load(plan['control_validation'])['full_gate_passed']
    assert a.page in [p['page'] for p in plan['pages']]
    assert (a.mode=='page' and a.replicate==0) or (a.mode=='null' and 0<=a.replicate<19)
    deps=CONTROL_DEPS+[PLAN,'experiments/long_substitution_unknown.py','transcriptions/pages.json','sources/manifest.json',
        'results/phase30_controls_validation.json','scripts/verify_long_substitution_controls.py','scripts/run_long_substitution_unknown.py']
    if a.mode=='null':deps+=['experiments/long_substitution_selection.json']
    ident=f'E084-{a.mode}-{a.page}'+(f'-{a.replicate:02}' if a.mode=='null' else '')
    registered(ident,plan|vars(a)|{'numpy':np.__version__},deps,lambda:run(a.mode,a.page,a.replicate))
