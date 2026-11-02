import argparse
import time
import numpy as np
from attack_support import load
from delay_two_controls import DEPS as CONTROL_DEPS
from delay_two_search import search
from periodic_key_controls import models
from section_key_support import join_pages,page_null
from ngram_arrays import dense_tables
from registry import registered
PLAN='experiments/delay_two_unknown_plan.json'


def run(mode,page,replicate):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    assert load(plan['control_validation'])['full_gate_passed']
    group=next(g for g in plan['groups'] if g['id']==page)
    cipher,spans=join_pages(group['page_ids']);proposals=None
    if mode=='null':
        assert page==load('experiments/delay_two_selection.json')['page']
        cipher,proposals=page_null(cipher,spans,plan['null_seed']+100*replicate,deadline)
    model,_,training=models();result=search(cipher,dense_tables(model),deadline)
    return {'experiment':'E079','mode':mode,'page':page,'replicate':replicate,'group':group,'parameters':plan,
        'ciphertext_indices':cipher,'page_spans':spans,'page_proposals':proposals,'training':training,
        'result':result,'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['page','null']);p.add_argument('page');p.add_argument('replicate',type=int);args=p.parse_args()
    assert args.page in load(PLAN)['section_ids'] and ((args.mode=='page' and args.replicate==0) or (args.mode=='null' and 0<=args.replicate<19))
    deps=CONTROL_DEPS+[PLAN,'experiments/delay_two_unknown.py','scripts/run_delay_two_unknown.py',
        'experiments/section_key_support.py','experiments/section_plan.json','transcriptions/pages.json',
        'results/phase28_controls_validation.json','scripts/verify_delay_two.py']
    if args.mode=='null':deps+=['experiments/delay_two_selection.json']
    ident=f'E079-{args.mode}-{args.page}'+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,load(PLAN)|vars(args)|{'numpy':np.__version__},deps,lambda:run(args.mode,args.page,args.replicate))
