"""Registered continuous section plaintext-autokey attacks and full nulls."""
import argparse
import time
import numpy as np
from affine_feedback_controls import DEPS
from affine_feedback_search import search
from periodic_key_controls import models
from attack_support import load
from section_key_support import join_pages,page_null
from ngram_arrays import dense_tables
from registry import registered
PLAN='experiments/affine_feedback_unknown_plan.json'


def run(mode,section,replicate):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    assert load(plan['control_validation'])['full_gate_passed'] and section in plan['section_ids']
    group=next(g for g in plan['groups'] if g['id']==section)
    cipher,spans=join_pages(group['page_ids']);proposals=None
    assert 200<=len(cipher)<=3316
    if mode=='null':
        assert section==load('experiments/affine_feedback_selection.json')['section']
        cipher,proposals=page_null(cipher,spans,plan['null_seed']+100*replicate,deadline)
    model,_,training=models();result=search(cipher,dense_tables(model),deadline)
    return {'experiment':'E073','mode':mode,'section':section,'group':group,'replicate':replicate,'parameters':plan,
        'page_spans':spans,'ciphertext_indices':cipher,'page_proposals':proposals,'training':training,
        'result':result,'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['section','null']);p.add_argument('section');p.add_argument('replicate',type=int,default=0,nargs='?');args=p.parse_args()
    assert (args.mode=='section' and args.replicate==0) or (args.mode=='null' and 0<=args.replicate<19)
    deps=DEPS+['experiments/section_key_support.py','experiments/section_plan.json','transcriptions/pages.json',PLAN,'experiments/affine_feedback_unknown.py','scripts/run_affine_feedback_unknown.py',
        'results/phase26_controls_validation.json','scripts/verify_affine_feedback.py']
    if args.mode=='null':deps+=['experiments/affine_feedback_selection.json']
    ident=f'E073-{args.mode}-{args.section}'+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,load(PLAN)|vars(args)|{'numpy':np.__version__},deps,lambda:run(args.mode,args.section,args.replicate))
