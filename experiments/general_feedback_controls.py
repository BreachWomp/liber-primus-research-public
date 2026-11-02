"""Registered blind controls for general plaintext-feedback coefficients."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_runes,to_indices
from periodic_key_controls import models,DEPS as BASE_DEPS
from autokey_extended_controls import control_source as old_source, DEPS as OLD_DEPS
from ngram_arrays import dense_tables
from liberprimus.general_feedback import encrypt
from general_feedback_search import search
from registry import registered
PLAN='experiments/general_feedback_plan.json'


def control_source(rows,index):
    if index>=12:
        source=old_source(rows,index-12)
        source['feedback_sign']%=29
        source['reused_input_control']=f'E062-control-{index-12}'
        return source
    chapter=('X','XI','XII')[index%3]
    start,length=((12750,200),(6800,300),(15000,729),(1000,3316))[index//3]
    m=(13,23,31)[index%3];a=(1,-1)[index%2];b=(2,7,14,27)[index%4]
    plain=[];ranges=[];cursor=0
    for row in rows:
        if row['chapter']!=chapter:continue
        piece=[x for w in row['words'] for x in w];lo=max(0,start-cursor);hi=min(len(piece),start+length-cursor)
        if lo<hi:
            plain+=piece[lo:hi];ranges.append({'source_character_range':row['source_character_range'],
                'paragraph':row['paragraph'],'paragraph_rune_range':[lo,hi]})
        cursor+=len(piece)
        if cursor>=start+length:break
    assert len(plain)==length
    rng=random.Random(3301066+index);key=[rng.randrange(29) for _ in range(m)]
    return {'chapter':chapter,'chapter_rune_range':[start,start+length],'source_ranges':ranges,
        'truth_runes':to_runes(plain),'injected_key':key,'cipher_sign':a,'feedback_sign':b,
        'ciphertext_indices':encrypt(plain,key,a,b)}


def run(kind,index):
    tick=time.perf_counter();deadline=tick+180
    model,rows,training=models();source=control_source(rows,index)
    if kind=='null':
        original=source['ciphertext_indices'];rng=random.Random(3302066)
        equal=lambda x:sum(a==b for a,b in zip(x,x[1:]))
        for proposals in range(1,100001):
            if time.perf_counter()>deadline:raise TimeoutError('Null deadline')
            middle=original[1:-1];rng.shuffle(middle);sample=original[:1]+middle+original[-1:]
            if equal(sample)==equal(original):break
        else:raise RuntimeError('Null rejection cap')
        source={'ciphertext_indices':sample,'proposals':proposals,'source_control':5}
    result=search(source['ciphertext_indices'],dense_tables(model),deadline)
    out={'experiment':f'E066-{kind}-{index}','kind':kind,'index':index,'parameters':load(PLAN),
        'training':training,'source':source,'result':result,'new_decryptions':[]}
    if kind=='control':
        top=result['top'][0];r=top['recipe']
        out['exact']=top['plaintext_runes']==source['truth_runes']
        out['injected_recipe_exact']=all(r[k]==source[s] for k,s in [('key_indices','injected_key'),('cipher_sign','cipher_sign'),('feedback_sign','feedback_sign')])
        injected=next(f for f in result['screening'] if (f['period'],f['cipher_sign'],f['feedback_sign'])==(len(source['injected_key']),source['cipher_sign'],source['feedback_sign']))
        out['injected_family_rank']=injected['rank'];out['injected_family_retained']=injected['rank']<=4
        out['correct_runes']=sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
    out['wall_seconds']=time.perf_counter()-tick
    print({k:out[k] for k in ('experiment','exact','injected_family_rank','correct_runes','wall_seconds') if k in out},flush=True)
    return out


DEPS=BASE_DEPS+OLD_DEPS+[PLAN,'experiments/general_feedback_controls.py','experiments/general_feedback_search.py',
    'experiments/general_feedback_factors.py','src/liberprimus/general_feedback.py','scripts/run_general_feedback_controls.py']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['control','null']);p.add_argument('index',type=int);args=p.parse_args()
    assert 0<=args.index<16 and (args.kind!='null' or args.index==5)
    registered(f'E066-{args.kind}-{args.index}',load(PLAN)|vars(args)|{'numpy':np.__version__},DEPS,lambda:run(args.kind,args.index))
