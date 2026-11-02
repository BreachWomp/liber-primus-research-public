import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices
from difference_substitution_bridge import DEPS as CONTROL_DEPS
from liberprimus.difference_substitution import differences
from terminated_benchmark import models
from terminated_search import SearchArrays,solve
from registry import registered
PLAN='experiments/difference_substitution_unknown_plan.json'


def run(mode,page,replicate):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    item=next(p for p in plan['pages'] if p['page']==page)
    source=next(p for p in load('transcriptions/pages.json') if p['id']==page)
    cipher=to_indices(source['runes']);proposals=None
    if mode=='null':
        assert page==load('experiments/difference_substitution_selection.json')['page']
        rng=random.Random(plan['null_seed']+100*replicate)
        target=sum(a==b for a,b in zip(cipher,cipher[1:]));original=cipher[:]
        for proposals in range(1,100001):
            if time.perf_counter()>deadline:raise TimeoutError('E086 null deadline')
            middle=original[1:-1];rng.shuffle(middle);cipher=original[:1]+middle+original[-1:]
            if sum(a==b for a,b in zip(cipher,cipher[1:]))==target:break
        else:raise TimeoutError('Null proposal cap')
    model,_,old,_,training=models();arrays=SearchArrays(model,old)
    delta=differences(cipher,0)
    result=solve(delta,item['segment_ends'],model,arrays,3303086+100*item['number'],deadline)
    return {'experiment':'E086','mode':mode,'page':page,'replicate':replicate,'parameters':plan,
        'ciphertext_indices':cipher,'difference_indices':delta,'iv':0,'segment_ends':item['segment_ends'],'null_proposals':proposals,
        'training':training,'result':result,'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['page','null']);p.add_argument('page');p.add_argument('replicate',type=int);a=p.parse_args()
    plan=load(PLAN);assert load(plan['control_validation'])['full_gate_passed']
    assert a.page in [p['page'] for p in plan['pages']]
    assert (a.mode=='page' and a.replicate==0) or (a.mode=='null' and 0<=a.replicate<19)
    deps=CONTROL_DEPS+[PLAN,'experiments/difference_substitution_unknown.py','transcriptions/pages.json','sources/manifest.json',
        'results/phase31_bridge_validation.json','scripts/verify_difference_substitution_bridge.py','scripts/run_difference_substitution_unknown.py']
    if a.mode=='null':deps+=['experiments/difference_substitution_selection.json']
    ident=f'E086-{a.mode}-{a.page}'+(f'-{a.replicate:02}' if a.mode=='null' else '')
    registered(ident,plan|vars(a)|{'numpy':np.__version__},deps,lambda:run(a.mode,a.page,a.replicate))
