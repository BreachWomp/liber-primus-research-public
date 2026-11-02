"""Frozen E052 solver on nine unknown groups and selection-corrected nulls."""
import argparse
import time
import numpy as np
from attack_support import load
from periodic_key_controls import models
from fragment_initialization_controls import DEPS
from fragment_initialization_search import search
from section_key_support import join_pages,page_null
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/fragment_initialization_unknown_plan.json'
SELECTION='experiments/fragment_initialization_selection.json'


def run(args):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    assert load(plan['control_validation'])['gate_passed']
    assert args.section in plan['section_ids']
    group=next(s for s in load('experiments/section_plan.json')['sections'] if s['id']==args.section)
    cipher,spans=join_pages(group['page_ids']);proposals=None
    if args.mode=='null':
        selection=load(SELECTION)
        assert args.section==selection['selected_section'] and 0<=args.replicate<plan['replicates']
        cipher,proposals=page_null(cipher,spans,plan['null_seed']+100*args.replicate,deadline)
    model,_,training=models();lookup=dense_tables(model)
    result=search(cipher,model,lookup,deadline,seed=plan['search_seed'])
    return {'experiment':'E053','parameters':vars(args),'section':args.section,'group':group,
            'page_spans':spans,'ciphertext_indices':cipher,'page_proposals':proposals,'training':training,
            'result':result,'score':result['top'][0]['score'],'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['section','null'],required=True)
    parser.add_argument('--section',required=True);parser.add_argument('--replicate',type=int,default=0)
    args=parser.parse_args();plan=load(PLAN)
    ident='E053-'+args.mode+'-'+args.section+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,vars(args)|{'numpy':np.__version__},DEPS+[PLAN,plan['control_validation'],
        'scripts/verify_phase18.py','scripts/run_fragment_initialization_unknown.py',
        'experiments/fragment_initialization_unknown.py','experiments/section_plan.json',
        'scripts/finalize_phase17.py']+([SELECTION] if args.mode=='null' else []),lambda:run(args))
