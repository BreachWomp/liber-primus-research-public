"""Explicit-key oracle diagnosis and reversible page-start F collisions."""
import math
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from periodic_key_controls import models
from long_phase_controls import DEPS as CONTROL_DEPS
from phase_key_search import optimize,replay
from liberprimus.periodic_key import encrypt
from registry import registered
PLAN='experiments/long_phase_diagnostic_plan.json'
VALIDATION='results/phase19_control_validation.json'


def run():
    tick=time.perf_counter();deadline=tick+180;model,_,training=models();controls=[];collisions=[]
    for entry in load(VALIDATION)['entries']:
        source_run=load(entry['output'])
        if source_run['kind']=='null':continue
        source=source_run['source'];cipher=source['ciphertext_indices'];truth=to_indices(source['truth_runes'])
        spans=source['page_spans'];key=source['injected_key'];sign=source['injected_sign'];skips=source['injected_skips'];phases=source['injected_phases']
        penalty=(len(key)*math.log(29)+cipher.count(0)*math.log(2)+(sum(s['runes']>0 for s in spans)-1)*math.log(len(key)))/len(cipher)
        score=lambda plain:sum(model.score(plain[s['start']:s['end']])*s['runes'] for s in spans if s['runes'])/len(cipher)-penalty
        row={'control_output':entry['output'],'kind':source_run['kind'],'index':source_run['index'],
             'original_exact':source_run['exact'],'truth_score':score(truth),'found_score':source_run['result']['top'][0]['score']}
        if not source_run['exact']:
            oracle=optimize(cipher,spans,key,sign,model,deadline)
            plain=replay(cipher,spans,oracle['key'],sign,oracle['skip_positions'],oracle['page_phases'])
            checks={'plaintext_exact':plain==truth,'key_exact':oracle['key']==key,
                    'mask_exact':oracle['skip_positions']==skips,'phases_exact':oracle['page_phases']==phases}
            row['known_key_oracle']={'truth_inputs':['injected_key_cycle','injected_sign'],'result':oracle|{'plaintext_runes':to_runes(plain)},
                'checks':checks,'exact':all(checks.values()),'correct_runes':sum(a==b for a,b in zip(plain,truth)),
                'oracle_minus_truth':oracle['score']-row['truth_score'],
                'error_positions':[i for i,(a,b) in enumerate(zip(plain,truth)) if a!=b]}
        controls.append(row);first=next(i for i,s in enumerate(spans) if s['runes'])
        for j,span in enumerate(spans):
            a,b=span['start'],span['end']
            if j==first or a==b or cipher[a]!=0:continue
            if time.perf_counter()>deadline:raise TimeoutError('Boundary diagnosis deadline')
            alternative_skips=sorted(set(skips)^{a});alternative_phases=phases[:]
            alternative_phases[j]=(phases[j]+(-1 if a in skips else 1))%len(key)
            alternative=replay(cipher,spans,key,sign,alternative_skips,alternative_phases)
            assert [i for i,(x,y) in enumerate(zip(truth,alternative)) if x!=y]==[a]
            for plaintext,mask,starts in ((truth,skips,phases),(alternative,alternative_skips,alternative_phases)):
                encoded=[]
                for s,p in zip(spans,starts):
                    x,y=s['start'],s['end']
                    encoded+=encrypt(plaintext[x:y],key[p:]+key[:p],sign,[i-x for i in mask if x<=i<y])
                assert encoded==cipher
            collisions.append({'control_output':entry['output'],'page_index':j,'ciphertext_position':a,
                'original_phase':phases[j],'alternative_phase':alternative_phases[j],
                'original_copied':a in skips,'alternative_skips':alternative_skips,'alternative_phases':alternative_phases,
                'original_symbol':truth[a],'alternative_symbol':alternative[a],
                'alternative_plaintext_runes':to_runes(alternative),'truth_score':score(truth),
                'alternative_score':score(alternative),'ciphertext_identical':True})
    return {'experiment':'E055','parameters':load(PLAN),'training':training,'controls':controls,
        'boundary_collisions':collisions,'unknown_sections_searched':0,'new_decryptions':[],
        'wall_seconds':time.perf_counter()-tick}


if __name__=='__main__':
    deps=CONTROL_DEPS+[PLAN,VALIDATION,'scripts/verify_phase19.py','experiments/long_phase_diagnostic.py']+[e['output'] for e in load(VALIDATION)['entries']]
    registered('E055-long-page-phase-diagnosis',load(PLAN)|{'numpy':np.__version__},deps,run)
