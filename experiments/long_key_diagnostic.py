"""Explicit oracle diagnoses of a failed long-key control, not recovery claims."""
import math
import time
import numpy as np
from attack_support import load,to_indices,cycle_key
from periodic_key_controls import models
from periodic_key_search import search as fixed_search
from joint_skip_search import optimize_schedule
from long_key_controls import DEPS as CONTROL_DEPS
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/long_key_diagnostic_plan.json'

def run():
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN);control=load(plan['control_output'])
    assert not control['gate_passed'];model,_,training=models();lookup=dense_tables(model);records=[]
    for source in control['controls']:
        cipher=source['ciphertext_indices'];plain=to_indices(source['truth_runes']);key=source['injected_key']
        top=source['result']['top'][0];target=(source['injected_sign'],cycle_key(key))
        truth_language=model.score(plain);truth_score=truth_language-(len(key)*math.log(29)+cipher.count(0)*math.log(2))/len(cipher)
        record={'chapter':source['chapter'],'key_length':len(key),'original_exact':source['exact'],
            'runes':len(cipher),'correct_runes':sum(a==b for a,b in zip(plain,to_indices(top['plaintext_runes']))),
            'truth_language_score':truth_language,'truth_score':truth_score,'found_score':top['score'],
            'truth_minus_found':truth_score-top['score'],
            'true_initial_seed_indices':[i for i,r in enumerate(source['result']['restarts']) if (r['initial']['sign'],cycle_key(r['initial']['key']))==target],
            'true_final_key_indices':[i for i,r in enumerate(source['result']['restarts']) if (r['final']['sign'],cycle_key(r['final']['key']))==target]}
        if not source['exact']:
            known=optimize_schedule(cipher,key,source['injected_sign'],model,deadline)
            record['known_key_oracle']={'truth_inputs':['injected_key','injected_sign'],'result':known,
                'mask_exact':known['skip_positions']==source['injected_skips'],'key_exact':known['key']==key}
            prefix=cipher[:1024];skips=[i for i in source['injected_skips'] if i<1024]
            result=fixed_search(prefix,lookup,deadline,seed=plan['seed'],oracle_skips=skips,periods=(len(key),))
            winner=result['top'][0]
            record['known_period_mask_oracle']={'truth_inputs':['injected_period','injected_prefix_mask'],
                'range':[0,len(prefix)],'period':len(key),'mask':skips,'result':result,
                'key_exact':winner['key']==key and winner['sign']==source['injected_sign'],
                'plaintext_exact':winner['plaintext_runes']==source['truth_runes'][:len(prefix)]}
        records.append(record)
    return {'experiment':'E050-long-key-diagnostic','parameters':plan,'training':training,'controls':records,
        'oracle_diagnosis_only':True,'unknown_sections_searched':0,'new_decryptions':[],
        'wall_seconds':time.perf_counter()-tick}

if __name__=='__main__':
    plan=load(PLAN);registered('E050-long-key-diagnostic',plan|{'numpy':np.__version__},
        CONTROL_DEPS+[PLAN,'experiments/long_key_diagnostic.py',plan['control_output']],run)
