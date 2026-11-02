"""Staged hybrid controls preserving both frozen searches."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from context_phase_controls import DEPS as BASE_DEPS
from periodic_key_controls import models
from hybrid_fragment_search import search
from attack_support import digest
from section_key_support import artificial_spans,page_null
from liberprimus.periodic_key import encrypt
from ngram_arrays import dense_tables
from registry import registered
PLAN='experiments/hybrid_fragment_plan.json'
VALIDATION='results/phase21_constraints_validation.json'
CONTROL_LIST=load(VALIDATION)['controls']
CACHE_ENTRIES={name:load(path)['entries'] for name,path in
    (('constrained',VALIDATION),('independent','results/phase20_blind_validation.json'))}
CACHE_PATHS=[e['output'] for entries in CACHE_ENTRIES.values() for e in entries]


def fresh(rows,index):
    chapter=('X','XI','XII')[index];plain=[];ranges=[];cursor=0
    for row in rows:
        if row['chapter']!=chapter:continue
        piece=[x for w in row['words'] for x in w];a=max(0,16850-cursor);b=min(len(piece),17579-cursor)
        if a<b:
            plain+=piece[a:b];ranges.append({'source_character_range':row['source_character_range'],
                'paragraph':row['paragraph'],'paragraph_rune_range':[a,b]})
        cursor+=len(piece)
        if cursor>=17579:break
    assert len(plain)==729
    m=(17,23,31)[index];sign=(1,-1,1)[index];rng=random.Random(3301060+index)
    key=[rng.randrange(1,29) for _ in range(m)];phases=[0,rng.randrange(m),rng.randrange(m)]
    spans=artificial_spans([262,266,201],chapter);mask_rng=random.Random(3304060+index);prob=(.25,.5,.75)[index]
    skips=[i for i,c in enumerate(plain) if c==0 and mask_rng.random()<prob];cipher=[]
    for s,p in zip(spans,phases):
        a,b=s['start'],s['end'];cipher+=encrypt(plain[a:b],key[p:]+key[:p],sign,[i-a for i in skips if a<=i<b])
    return {'chapter':chapter,'chapter_rune_range':[16850,17579],'source_ranges':ranges,'truth_runes':to_runes(plain),
        'page_spans':spans,'ciphertext_indices':cipher,'injected_key':key,'injected_sign':sign,'injected_skips':skips,
        'injected_phases':phases,'F_copy_probability':prob}


def run(kind,index):
    tick=time.perf_counter();deadline=tick+180;assert len(CONTROL_LIST)==18
    model,rows,training=models();lookup=dense_tables(model)
    source=fresh(rows,index) if kind in ('fresh','null') else load(CONTROL_LIST[index]['output'])['source']
    if kind=='null':
        cipher,proposals=page_null(source['ciphertext_indices'],source['page_spans'],3302060,deadline)
        source={'ciphertext_indices':cipher,'page_spans':source['page_spans'],'page_proposals':proposals,'source_index':2,'source_kind':'fresh'}
    cached={}
    for name,entries in CACHE_ENTRIES.items():
        for entry in entries:
            assert digest(entry['output'])==entry['sha256']
            old=load(entry['output'])
            if (old['source']['ciphertext_indices']==source['ciphertext_indices'] and
                old['source']['page_spans']==source['page_spans'] and old['training']==training):
                cached[name]={'result':old['result'],'output':entry['output'],'sha256':entry['sha256']};break
    result=search(source['ciphertext_indices'],source['page_spans'],model,lookup,deadline,cached=cached)
    record={'experiment':f'E060-{kind}-{index}','kind':kind,'index':index,'parameters':load(PLAN),'training':training,
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


DEPS=BASE_DEPS+[PLAN,VALIDATION,'results/phase20_blind_validation.json',
    'experiments/context_blind_search.py','experiments/constrained_fragment_search.py',
    'src/liberprimus/fragment_constraints.py','experiments/hybrid_fragment_search.py',
    'experiments/hybrid_fragment_controls.py','scripts/run_hybrid_fragment_controls.py',
    'scripts/verify_constrained_fragments.py','scripts/verify_context_blind.py']+CACHE_PATHS
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['fresh','regression','null']);parser.add_argument('index',type=int);args=parser.parse_args()
    assert 0<=args.index<(18 if args.kind=='regression' else 3)
    assert args.kind!='null' or args.index==2
    registered(f'E060-{args.kind}-{args.index}',load(PLAN)|{'kind':args.kind,'index':args.index,'numpy':np.__version__},DEPS,lambda:run(args.kind,args.index))
