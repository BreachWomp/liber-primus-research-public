"""Staged blind controls for ciphertext-constrained fragment phases."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from context_phase_controls import DEPS as BASE_DEPS
from periodic_key_controls import models
from constrained_fragment_search import search
from section_key_support import artificial_spans,page_null
from liberprimus.periodic_key import encrypt
from ngram_arrays import dense_tables
from registry import registered
PLAN='experiments/constrained_fragment_plan.json'
VALIDATION='results/phase20_context_validation.json'
SOURCE=load(VALIDATION)['entry']['output']


def fresh(rows,index):
    chapter=('X','XI','XII')[index];plain=[];ranges=[];cursor=0
    for row in rows:
        if row['chapter']!=chapter:continue
        piece=[x for w in row['words'] for x in w];a=max(0,16000-cursor);b=min(len(piece),16729-cursor)
        if a<b:
            plain+=piece[a:b];ranges.append({'source_character_range':row['source_character_range'],
                'paragraph':row['paragraph'],'paragraph_rune_range':[a,b]})
        cursor+=len(piece)
        if cursor>=16729:break
    assert len(plain)==729
    m=(17,23,31)[index];sign=(1,-1,1)[index];rng=random.Random(3301058+index)
    key=[rng.randrange(1,29) for _ in range(m)];phases=[0,rng.randrange(m),rng.randrange(m)]
    spans=artificial_spans([262,266,201],chapter);mask_rng=random.Random(3304058+index);prob=(.25,.5,.75)[index]
    skips=[i for i,c in enumerate(plain) if c==0 and mask_rng.random()<prob];cipher=[]
    for s,p in zip(spans,phases):
        a,b=s['start'],s['end'];cipher+=encrypt(plain[a:b],key[p:]+key[:p],sign,[i-a for i in skips if a<=i<b])
    return {'chapter':chapter,'chapter_rune_range':[16000,16729],'source_ranges':ranges,'truth_runes':to_runes(plain),
        'page_spans':spans,'ciphertext_indices':cipher,'injected_key':key,'injected_sign':sign,'injected_skips':skips,
        'injected_phases':phases,'F_copy_probability':prob}


def run(kind,index):
    tick=time.perf_counter();deadline=tick+180;assert load(VALIDATION)['oracle_gate_passed']
    model,rows,training=models();lookup=dense_tables(model)
    source=fresh(rows,index) if kind in ('fresh','null') else load(SOURCE)['controls'][index if kind=='regression' else 12+index]['source']
    if kind=='null':
        cipher,proposals=page_null(source['ciphertext_indices'],source['page_spans'],3302058,deadline)
        source={'ciphertext_indices':cipher,'page_spans':source['page_spans'],'page_proposals':proposals,'source_index':2,'source_kind':'fresh'}
    result=search(source['ciphertext_indices'],source['page_spans'],model,lookup,deadline)
    record={'experiment':f'E058-{kind}-{index}','kind':kind,'index':index,'parameters':load(PLAN),'training':training,
        'source':source,'result':result,'unknown_sections_searched':0,'new_decryptions':[]}
    if kind!='null':
        top=result['top'][0];record['checks']={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
            'key_exact':top['key']==source['injected_key'] and top['sign']==source['injected_sign'],
            'mask_exact':top['skip_positions']==source['injected_skips'],'phases_exact':top['page_phases']==source['injected_phases']}
        record['exact']=all(record['checks'].values());truth=to_indices(source['truth_runes']);plain=to_indices(top['plaintext_runes'])
        record['correct_runes']=sum(a==b for a,b in zip(truth,plain))
    record['wall_seconds']=time.perf_counter()-tick
    print({k:record[k] for k in ('experiment','wall_seconds','checks','correct_runes') if k in record},flush=True)
    return record


DEPS=BASE_DEPS+[PLAN,VALIDATION,SOURCE,'scripts/verify_context_calibration.py','experiments/constrained_fragment_search.py','src/liberprimus/fragment_constraints.py',
    'experiments/constrained_fragment_controls.py','scripts/run_constrained_fragment_controls.py']
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['fresh','regression','stress','null']);parser.add_argument('index',type=int);args=parser.parse_args()
    assert 0<=args.index<(12 if args.kind=='regression' else 3)
    assert args.kind!='null' or args.index==2
    registered(f'E058-{args.kind}-{args.index}',load(PLAN)|{'kind':args.kind,'index':args.index,'numpy':np.__version__},DEPS,lambda:run(args.kind,args.index))
