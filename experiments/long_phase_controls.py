"""Page-phase long-key controls, new ranges and unchanged E052 regressions."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from fragment_initialization_controls import DEPS as BASE_DEPS
from periodic_key_controls import models
from long_phase_search import search
from section_key_support import join_pages,artificial_spans,page_null
from liberprimus.periodic_key import encrypt
from ngram_arrays import dense_tables
from registry import registered
PLAN='experiments/long_phase_plan.json'
VALIDATION='results/phase18_control_validation.json'
DEPS=BASE_DEPS+[PLAN,VALIDATION,'experiments/long_phase_search.py','experiments/long_phase_controls.py',
                'scripts/run_long_phase_controls.py']+[e['output'] for e in load(VALIDATION)['entries']]


def fresh(rows,index):
    chapter=('X','XI','XII')[index%3];period=(17,23,31)[index%3];sign=(1,-1,1)[index%3]
    offset=6000 if index<3 else 8000;length=729 if index<3 else 3316
    ids=[f'LP2-{i:02}' for i in (range(3) if index<3 else range(40,56))]
    _,original=join_pages(ids);spans=artificial_spans([s['runes'] for s in original],chapter)
    plain=[];ranges=[];cursor=0
    for row in rows:
        if row['chapter']!=chapter:continue
        piece=[x for word in row['words'] for x in word];a=max(0,offset-cursor);b=min(len(piece),offset+length-cursor)
        if a<b:
            plain+=piece[a:b];ranges.append({'source_character_range':row['source_character_range'],
                'paragraph':row['paragraph'],'paragraph_rune_range':[a,b]})
        cursor+=len(piece)
        if cursor>=offset+length:break
    assert len(plain)==length==spans[-1]['end']
    rng=random.Random(3301054+index);key=[rng.randrange(1,29) for _ in range(period)]
    phases=[];first=True
    for span in spans:
        empty=span['start']==span['end'];phases.append(0 if empty or first else rng.randrange(period))
        if not empty:first=False
    mask_rng=random.Random(3304054+index);prob=(.25,.5,.75)[index%3]
    skips=[i for i,c in enumerate(plain) if c==0 and mask_rng.random()<prob];cipher=[]
    for span,phase in zip(spans,phases):
        a,b=span['start'],span['end']
        cipher+=encrypt(plain[a:b],key[phase:]+key[:phase],sign,[i-a for i in skips if a<=i<b])
    return {'chapter':chapter,'chapter_rune_range':[offset,offset+length],'source_ranges':ranges,
        'source_span_page_ids':ids,'page_spans':spans,'truth_runes':to_runes(plain),'ciphertext_indices':cipher,
        'injected_key':key,'injected_sign':sign,'injected_skips':skips,'injected_phases':phases,'F_copy_probability':prob}


def regression(index):
    entries=[e for e in load(VALIDATION)['entries'] if 'null' not in e['id']]
    prior=load(entries[index]['output']);source=dict(prior['source']);cursor=0;phases=[]
    for span in source['page_spans']:
        a,b=span['start'],span['end'];phases.append(cursor%len(source['injected_key']) if a!=b else 0)
        cursor+=b-a-sum(a<=i<b for i in source['injected_skips'])
    source['injected_phases']=phases;source['regression_output']=entries[index]['output']
    return source


def run(kind,index):
    tick=time.perf_counter();deadline=tick+180;model,rows,training=models();lookup=dense_tables(model)
    source=regression(index) if kind=='regression' else fresh(rows,index)
    if kind=='null':
        cipher,proposals=page_null(source['ciphertext_indices'],source['page_spans'],3302054,deadline)
        source={'chapter':source['chapter'],'ciphertext_indices':cipher,'page_spans':source['page_spans'],
                'page_proposals':proposals,'source_index':index,'source_kind':'fresh'}
    result=search(source['ciphertext_indices'],source['page_spans'],model,lookup,deadline)
    record={'experiment':f'E054-{kind}-{index}','parameters':load(PLAN),'kind':kind,'index':index,
        'training':training,'source':source,'result':result,'unknown_sections_searched':0,'new_decryptions':[]}
    if kind!='null':
        top=result['top'][0];record['checks']={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
            'key_exact':top['key']==source['injected_key'] and top['sign']==source['injected_sign'],
            'mask_exact':top['skip_positions']==source['injected_skips'],'phases_exact':top['page_phases']==source['injected_phases']}
        record['exact']=all(record['checks'].values())
        record['correct_runes']=sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
    record['wall_seconds']=time.perf_counter()-tick
    print({k:record[k] for k in ('experiment','wall_seconds','checks','correct_runes') if k in record},flush=True)
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['fresh','regression','null']);parser.add_argument('index',type=int,choices=range(6));args=parser.parse_args()
    if args.kind=='null' and args.index!=2:parser.error('Only freshcase2 null preregistered')
    registered(f'E054-{args.kind}-{args.index}',load(PLAN)|{'kind':args.kind,'index':args.index,'numpy':np.__version__},DEPS,lambda:run(args.kind,args.index))
