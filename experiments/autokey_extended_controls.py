"""Registered source-excluded long-seed plaintext-autokey controls."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_runes,to_indices
from periodic_key_controls import models,DEPS as BASE_DEPS
from plaintext_autokey_attack import invert
from conditional_attack_null import conditional_shuffle
from ngram_arrays import dense_tables
from autokey_extended_search import search
from autokey_beam import SIGNS
from registry import registered
PLAN='experiments/autokey_extended_plan.json'


def control_source(rows,index):
    chapter=('X','XI','XII')[index%3]
    start,length=((6800,300),(7300,300),(12750,200),(15000,729))[index//3]
    period=((13,23,31),(4,8,12),(13,23,31),(13,23,31))[index//3][index%3]
    plain=[];ranges=[];cursor=0
    for row in rows:
        if row['chapter']!=chapter:continue
        piece=[x for w in row['words'] for x in w];a=max(0,start-cursor);b=min(len(piece),start+length-cursor)
        if a<b:
            plain+=piece[a:b];ranges.append({'source_character_range':row['source_character_range'],
                'paragraph':row['paragraph'],'paragraph_rune_range':[a,b]})
        cursor+=len(piece)
        if cursor>=start+length:break
    assert len(plain)==length
    rng=random.Random(3301062+index);key=[rng.randrange(29) for _ in range(period)];cs,ks=SIGNS[index%4]
    cipher=invert(plain,key,cs,ks,[])
    return {'chapter':chapter,'chapter_rune_range':[start,start+length],'source_ranges':ranges,
        'truth_runes':to_runes(plain),'injected_key':key,'cipher_sign':cs,'feedback_sign':ks,
        'ciphertext_indices':cipher}


def run(kind,index):
    tick=time.perf_counter();deadline=tick+180
    model,rows,training=models();lookup=dense_tables(model);source=control_source(rows,index)
    if kind=='null':
        cipher,proposals=conditional_shuffle(source['ciphertext_indices'],random.Random(3302062),deadline=deadline)
        source={'ciphertext_indices':cipher,'proposals':proposals,'source_control':2}
    result=search(source['ciphertext_indices'],lookup,deadline)
    out={'experiment':f'E062-{kind}-{index}','kind':kind,'index':index,'parameters':load(PLAN),
        'training':training,'source':source,'result':result,'new_decryptions':[]}
    if kind=='control':
        top=result['top'][0];recipe=top['recipe']
        out['exact']=top['plaintext_runes']==source['truth_runes']
        out['injected_recipe_exact']=(recipe['key_indices']==source['injected_key'] and recipe['cipher_sign']==source['cipher_sign'] and recipe['feedback_sign']==source['feedback_sign'])
        out['correct_runes']=sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
    out['wall_seconds']=time.perf_counter()-tick
    print({k:out[k] for k in ('experiment','exact','correct_runes','wall_seconds') if k in out},flush=True)
    return out


DEPS=BASE_DEPS+[PLAN,'experiments/autokey_extended_controls.py','experiments/autokey_extended_search.py',
    'experiments/autokey_beam.py','experiments/short_seed_autokey.py','experiments/plaintext_autokey_attack.py',
    'experiments/ciphertext_autokey_scan.py','src/liberprimus/autokey_chains.py','scripts/run_autokey_extended_controls.py']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['control','null']);p.add_argument('index',type=int);args=p.parse_args()
    assert 0<=args.index<12 and (args.kind!='null' or args.index==2)
    registered(f'E062-{args.kind}-{args.index}',load(PLAN)|{'kind':args.kind,'index':args.index,'numpy':np.__version__},DEPS,lambda:run(args.kind,args.index))
