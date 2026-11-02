"""Fresh-key long continuous-stream controls; frozen E062 solver."""
import argparse
import random
import time
import numpy as np
from autokey_extended_controls import DEPS as BASE_DEPS
from autokey_extended_search import search
from periodic_key_controls import models
from attack_support import load,to_runes,to_indices
from ngram_arrays import dense_tables
from plaintext_autokey_attack import invert
from section_key_support import join_pages,artificial_spans,page_null
from registry import registered
PLAN='experiments/autokey_section_plan.json'


def control_source(rows,index):
    chapter=('X','XI','XII','X')[index];start=1000 if index<3 else 5400;length=3316
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
    group=next(g for g in load('experiments/section_plan.json')['sections'] if g['id']=='LP2-40_55')
    _,template=join_pages(group['page_ids']);spans=artificial_spans([s['runes'] for s in template],chapter)
    m=(13,23,31,32)[index];rng=random.Random(3301064+index);key=[rng.randrange(29) for _ in range(m)]
    cs,ks=((1,-1),(1,1),(-1,-1),(-1,1))[index];cipher=invert(plain,key,cs,ks,[])
    return {'chapter':chapter,'chapter_rune_range':[start,start+length],'source_ranges':ranges,
        'truth_runes':to_runes(plain),'injected_key':key,'cipher_sign':cs,'feedback_sign':ks,
        'ciphertext_indices':cipher,'page_spans':spans,'template_group':'LP2-40_55'}


def run(kind,index):
    tick=time.perf_counter();deadline=tick+180;model,rows,training=models();source=control_source(rows,index)
    if kind=='null':
        cipher,proposals=page_null(source['ciphertext_indices'],source['page_spans'],3302064,deadline)
        source={'ciphertext_indices':cipher,'page_spans':source['page_spans'],'page_proposals':proposals,'source_control':3}
    result=search(source['ciphertext_indices'],dense_tables(model),deadline)
    out={'experiment':f'E064-{kind}-{index}','kind':kind,'index':index,'parameters':load(PLAN),'training':training,
        'source':source,'result':result,'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}
    if kind=='control':
        top=result['top'][0];r=top['recipe'];out['exact']=top['plaintext_runes']==source['truth_runes']
        out['injected_recipe_exact']=(r['key_indices']==source['injected_key'] and r['cipher_sign']==source['cipher_sign'] and r['feedback_sign']==source['feedback_sign'])
        out['correct_runes']=sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
    print({k:out[k] for k in ('experiment','exact','correct_runes','wall_seconds') if k in out},flush=True)
    return out


DEPS=BASE_DEPS+[PLAN,'experiments/autokey_section_controls.py','experiments/section_key_support.py',
    'experiments/section_plan.json','transcriptions/pages.json','scripts/run_autokey_section_controls.py',
    'results/phase22_controls_validation.json','scripts/verify_autokey_extended.py']
DEPS += [r['output'] for r in load('results/phase22_controls_validation.json')['controls']]
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['control','null']);p.add_argument('index',type=int);args=p.parse_args()
    assert 0<=args.index<4 and (args.kind!='null' or args.index==3)
    registered(f'E064-{args.kind}-{args.index}',load(PLAN)|vars(args)|{'numpy':np.__version__},DEPS,lambda:run(args.kind,args.index))
