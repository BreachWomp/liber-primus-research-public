"""Explicit-key paired calibration of continuous versus reset language context."""
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from periodic_key_controls import models
from long_phase_controls import DEPS as PREVIOUS_DEPS
from context_phase_search import optimize,alternatives
from phase_key_search import optimize as reset_optimize,replay
from section_key_support import artificial_spans,page_null
from liberprimus.periodic_key import encrypt
from registry import registered
PLAN='experiments/context_phase_plan.json'
OLD='results/phase19_control_validation.json'
DIAG='results/E055-long-page-phase-diagnosis-29c3d4f36f52.json'


def fresh(rows,index):
    chapter=('X','XI','XII')[index];plain=[];ranges=[];cursor=0
    for row in rows:
        if row['chapter']!=chapter:continue
        piece=[x for word in row['words'] for x in word];a=max(0,12000-cursor);b=min(len(piece),12729-cursor)
        if a<b:
            plain+=piece[a:b];ranges.append({'source_character_range':row['source_character_range'],
                'paragraph':row['paragraph'],'paragraph_rune_range':[a,b]})
        cursor+=len(piece)
        if cursor>=12729:break
    assert len(plain)==729
    boundary=next(i for i in range(262,294) if plain[i]!=0);spans=artificial_spans([boundary,528-boundary,201],chapter)
    m=(17,23,31)[index];sign=(1,-1,1)[index];rng=random.Random(3301056+index)
    key=[rng.randrange(1,29) for _ in range(m)];key[0]=plain[boundary];phases=[0,0,rng.randrange(m)]
    mask_rng=random.Random(3304056+index);prob=(.25,.5,.75)[index]
    skips=[i for i,c in enumerate(plain) if c==0 and mask_rng.random()<prob];cipher=[]
    for s,p in zip(spans,phases):
        a,b=s['start'],s['end'];cipher+=encrypt(plain[a:b],key[p:]+key[:p],sign,[i-a for i in skips if a<=i<b])
    assert cipher[boundary]==0 and boundary not in skips
    return {'chapter':chapter,'chapter_rune_range':[12000,12729],'source_ranges':ranges,'truth_runes':to_runes(plain),
        'page_spans':spans,'ciphertext_indices':cipher,'injected_key':key,'injected_sign':sign,'injected_skips':skips,
        'injected_phases':phases,'stress_boundary':boundary,'F_copy_probability':prob}


def candidate(source,row):
    plain=replay(source['ciphertext_indices'],source['page_spans'],row['key'],row['sign'],row['skip_positions'],row['page_phases'])
    return row|{'plaintext_runes':to_runes(plain)}


def checks(source,row):
    return {'plaintext_exact':row['plaintext_runes']==source['truth_runes'],
        'key_exact':row['key']==source['injected_key'] and row['sign']==source['injected_sign'],
        'mask_exact':row['skip_positions']==source['injected_skips'],'phases_exact':row['page_phases']==source['injected_phases']}


def run():
    tick=time.perf_counter();deadline=tick+180;model,rows,training=models();controls=[]
    prior_oracles={r['control_output']:r['known_key_oracle']['result'] for r in load(DIAG)['controls'] if 'known_key_oracle' in r}
    inputs=[]
    for entry in load(OLD)['entries']:
        old=load(entry['output'])
        if old['kind']=='null':continue
        baseline=prior_oracles.get(entry['output'],old['result']['top'][0])
        inputs.append(('regression',len(inputs),old['source'],entry['output'],baseline))
    inputs += [('fresh',i,fresh(rows,i),None,None) for i in range(3)]
    for kind,index,source,path,baseline in inputs:
        cipher=source['ciphertext_indices'];spans=source['page_spans'];key=source['injected_key'];sign=source['injected_sign']
        reset=candidate(source,baseline if baseline is not None else reset_optimize(cipher,spans,key,sign,model,deadline))
        coupled=candidate(source,optimize(cipher,spans,key,sign,model,deadline))
        c=checks(source,coupled);controls.append({'kind':kind,'index':index,'source':source,'source_output':path,
            'truth_inputs':['injected_key_cycle','injected_sign'],'baseline_reused':baseline is not None,
            'reset':reset,'coupled':coupled,'reset_checks':checks(source,reset),'coupled_checks':c,
            'coupled_exact':all(c.values()),'alternatives':alternatives(cipher,spans,coupled,model)})
        print({'kind':kind,'index':index,'coupled_checks':c,'seconds':time.perf_counter()-tick},flush=True)
    original=inputs[-1][2];cipher,proposals=page_null(original['ciphertext_indices'],original['page_spans'],3302056,deadline)
    source={'ciphertext_indices':cipher,'page_spans':original['page_spans']};key=original['injected_key'];sign=original['injected_sign']
    null={'source_kind':'fresh','source_index':2,'ciphertext_indices':cipher,'page_spans':source['page_spans'],'page_proposals':proposals,
        'truth_inputs':['source_injected_key_cycle','source_injected_sign'],
        'reset':candidate(source,reset_optimize(cipher,source['page_spans'],key,sign,model,deadline)),
        'coupled':candidate(source,optimize(cipher,source['page_spans'],key,sign,model,deadline))}
    return {'experiment':'E056','parameters':load(PLAN),'training':training,'controls':controls,'nulls':[null],
        'oracle_gate_passed':all(r['coupled_exact'] for r in controls),'blind_gate_passed':False,
        'unknown_sections_searched':0,'new_decryptions':[],'wall_seconds':time.perf_counter()-tick}


DEPS=PREVIOUS_DEPS+[PLAN,OLD,DIAG,'experiments/context_phase_search.py','experiments/context_phase_controls.py',
    'scripts/run_context_calibration.py']+[e['output'] for e in load(OLD)['entries']]
if __name__=='__main__':registered('E056-context-coupled-calibration',load(PLAN)|{'numpy':np.__version__},DEPS,run)
