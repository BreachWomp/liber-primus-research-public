import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices
from terminated_benchmark import models,DEPS as BENCH_DEPS
from terminated_search import SearchArrays,solve
from substitution_prototype import AUDIT
from registry import registered
PLAN='experiments/long_substitution_controls_plan.json'


def source(rows,index):
    chapter=('X','XI','XII')[index%3];block=index//3
    minimum=(200,300,500,729)[block]
    r=[r for r in rows if r['chapter']==chapter and sum(map(len,r['words']))>=760][2+block]
    plain=[];ends=[]
    for word in r['words']:
        plain+=word;ends.append(len(plain))
        if len(plain)>=minimum:break
    metadata={'chapter':chapter,'paragraph':r['paragraph'],'source_character_range':r['source_character_range'],
        'minimum_runes':minimum,'word_count':len(ends),'eligible_paragraph_index':2+block}
    permutation=list(range(29));random.Random(3301083+index).shuffle(permutation)
    return metadata|{'plaintext_indices':plain,'segment_ends':ends,'permutation_plain_to_cipher':permutation,
        'ciphertext_indices':[permutation[x] for x in plain]}


def run(kind,index,replicate):
    tick=time.perf_counter();deadline=tick+180
    model,_,old,rows,training=models();arrays=SearchArrays(model,old);s=source(rows,index)
    cipher=s['ciphertext_indices'][:]
    if kind=='null':random.Random(3302083+replicate).shuffle(cipher)
    result=solve(cipher,s['segment_ends'],model,arrays,3303083+100*index,deadline)
    plain=to_indices(result['top']['plaintext_runes'])
    return {'experiment':'E083','kind':kind,'index':index,'replicate':replicate,'parameters':load(PLAN),
        'source':s,'ciphertext_indices':cipher,'training':training,'result':result,
        'exact':plain==s['plaintext_indices'] if kind=='control' else None,
        'correct_positions':sum(a==b for a,b in zip(plain,s['plaintext_indices'])) if kind=='control' else None,
        'truth_score':model.score(s['plaintext_indices'],s['segment_ends']) if kind=='control' else None,
        'wall_seconds':time.perf_counter()-tick,'unknown_pages_searched':0,'new_decryptions':[]}


DEPS=BENCH_DEPS+[PLAN,'experiments/long_substitution_controls.py','experiments/terminated_search.py',
    'experiments/boundary_substitution.py','experiments/word_arrays.py',
    'results/phase29_benchmark_validation.json','scripts/verify_terminated_benchmark.py','scripts/run_long_substitution_controls.py','scripts/long_substitution_supervisor.py']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['control','null']);p.add_argument('index',type=int);p.add_argument('replicate',type=int);a=p.parse_args()
    assert 0<=a.index<12 and ((a.kind=='control' and a.replicate==0) or (a.kind=='null' and a.index==0 and 0<=a.replicate<3))
    assert load(load(PLAN)['benchmark_validation'])['gate_passed']
    ident=f'E083-{a.kind}-{a.index}'+(f'-{a.replicate}' if a.kind=='null' else '')
    registered(ident,load(PLAN)|vars(a)|{'numpy':np.__version__},DEPS,lambda:run(a.kind,a.index,a.replicate))
