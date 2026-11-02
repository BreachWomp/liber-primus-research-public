"""Unknown-page and fully reoptimized null runs for the gated joint solver."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices
from periodic_key_controls import models
from joint_skip_external import DEPS as EXTERNAL_DEPS
from joint_skip_search import search
from conditional_attack_null import conditional_shuffle
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/joint_skip_unknown_plan.json'
SELECTION='experiments/joint_skip_selection.json'


def run(args):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    assert all(load(plan[k])['gate_passed'] for k in ('control_output','historical_control_output'))
    model,_,training=models();lookup=dense_tables(model)
    page=next(p for p in load('transcriptions/pages.json') if p['id']==args.page)
    assert page['edition']=='LP2' and page['page']<56 and page['page']!=50
    cipher=to_indices(page['runes']);proposals=None
    if args.mode=='null':
        selection=load(SELECTION)
        assert args.page==selection['selected_page'] and 0<=args.replicate<plan['replicates']
        cipher,proposals=conditional_shuffle(cipher,random.Random(plan['null_seed']+args.replicate),deadline=deadline)
    result=search(cipher,model,lookup,deadline,seed=plan['search_seed'])
    return {'experiment':'E042-joint-key-skip-unknown','parameters':vars(args),'page':args.page,
            'ciphertext_indices':cipher,'training':training,'result':result,
            'score':result['top'][0]['score'],'shuffle_proposals':proposals,
            'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


DEPS=EXTERNAL_DEPS+[PLAN,'experiments/joint_skip_unknown.py','transcriptions/pages.json',
                   'results/E041-joint-key-skip-external-709077b9a6f8.json']

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['page','null'],required=True)
    parser.add_argument('--page',required=True);parser.add_argument('--replicate',type=int,default=0);args=parser.parse_args()
    ident='E042-'+args.mode+'-'+args.page+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,vars(args)|{'numpy':np.__version__},DEPS+([SELECTION] if args.mode=='null' else []),lambda:run(args))
