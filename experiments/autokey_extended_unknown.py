"""Registered E063 single-page attacks and matched endpoint-preserving nulls."""
import argparse
import random
import time
import numpy as np
from autokey_extended_controls import DEPS
from autokey_extended_search import search
from periodic_key_controls import models
from attack_support import load,to_indices
from ngram_arrays import dense_tables
from registry import registered
PLAN='experiments/autokey_extended_unknown_plan.json'


def run(mode,page_id,replicate):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    assert load(plan['control_validation'])['full_gate_passed'] and page_id in plan['page_ids']
    page=next(p for p in load('transcriptions/pages.json') if p['id']==page_id)
    cipher=to_indices(page['runes']);proposals=0
    if mode=='null':
        assert page_id==load('experiments/autokey_extended_selection.json')['page']
        rng=random.Random(plan['null_seed']+replicate);original=cipher[:]
        doublets=lambda a:sum(x==y for x,y in zip(a,a[1:]))
        for proposals in range(1,100001):
            middle=original[1:-1];rng.shuffle(middle);cipher=original[:1]+middle+original[-1:]
            if doublets(cipher)==doublets(original):break
        else:raise TimeoutError('Null rejection cap')
    model,_,training=models();result=search(cipher,dense_tables(model),deadline)
    return {'experiment':'E063','mode':mode,'page':page_id,'replicate':replicate,'parameters':plan,
        'source_refs':page['source_refs'],'ciphertext_indices':cipher,'proposals':proposals,'training':training,
        'result':result,'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['page','null']);p.add_argument('page');p.add_argument('replicate',type=int,default=0,nargs='?');args=p.parse_args()
    assert (args.mode=='page' and args.replicate==0) or (args.mode=='null' and 0<=args.replicate<19)
    deps=DEPS+[PLAN,'experiments/autokey_extended_unknown.py','scripts/run_autokey_extended_unknown.py',
        'results/phase22_controls_validation.json','scripts/verify_autokey_extended.py','transcriptions/pages.json']
    if args.mode=='null':deps+=['experiments/autokey_extended_selection.json']
    ident=f'E063-{args.mode}-{args.page}'+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,load(PLAN)|vars(args)|{'numpy':np.__version__},deps,lambda:run(args.mode,args.page,args.replicate))
