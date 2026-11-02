"""Bounded page-phase search and fully reoptimized page-conditional nulls."""
import argparse
import time
import numpy as np
from attack_support import load
from periodic_key_controls import models
from phase_key_controls import DEPS as CONTROL_DEPS
from phase_key_search import search
from section_key_support import join_pages,page_null
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/phase_key_unknown_plan.json'
SELECTION='experiments/phase_key_selection.json'

def run(args):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    assert load(plan['control_output'])['gate_passed']
    group=next(s for s in load('experiments/section_plan.json')['sections'] if s['id']==args.section)
    cipher,spans=join_pages(group['page_ids']);proposals=None
    if args.mode=='null':
        selection=load(SELECTION)
        assert args.section==selection['selected_section'] and 0<=args.replicate<plan['replicates']
        cipher,proposals=page_null(cipher,spans,plan['null_seed']+100*args.replicate,deadline)
    model,_,training=models();lookup=dense_tables(model)
    result=search(cipher,spans,model,lookup,deadline,seed=plan['search_seed'])
    return {'experiment':'E048-page-phase-unknown','parameters':vars(args),'section':args.section,
        'group':group,'page_spans':spans,'ciphertext_indices':cipher,'page_proposals':proposals,
        'training':training,'result':result,'score':result['top'][0]['score'],
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['section','null'],required=True)
    parser.add_argument('--section',required=True);parser.add_argument('--replicate',type=int,default=0)
    args=parser.parse_args();plan=load(PLAN)
    ident='E048-'+args.mode+'-'+args.section+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,vars(args)|{'numpy':np.__version__},CONTROL_DEPS+[PLAN,
        'experiments/phase_key_unknown.py',plan['control_output']]+([SELECTION] if args.mode=='null' else []),lambda:run(args))
