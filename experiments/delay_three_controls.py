"""E075 fresh three-rune keys on excluded-source controls and fixed null."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from periodic_key_controls import models
from bilinear_feedback_controls import control_source as old_source,DEPS as OLD_DEPS
from delay_three_benchmark import DEPS as BENCH_DEPS,PLAN
from delay_three_search import search
from liberprimus.affine_feedback import encrypt
from ngram_arrays import dense_tables
from registry import registered


def control_source(rows,index):
    base_index=(index%3 if index<9 else 3+index%3) if index<12 else (0,3,6,11)[index-12]
    base=old_source(rows,base_index)
    n=(66,95,200,300)[index//3] if index<12 else len(base['ciphertext_indices'])
    plain=to_indices(base['truth_runes'])[:n]
    a,b=((2,7,14,27)[index%4],(1,3,15,28)[index%4]) if index<12 else ((1,1),(1,28),(28,1),(28,28))[index-12]
    c=(5*index+1)%28+1 if index<12 else 0
    rng=random.Random(3301075+index);key=[rng.randrange(29) for _ in range(3)]
    return {'base_control_index':base_index,'base_source':base,'take_runes':n,'truth_runes':to_runes(plain),
        'injected_key':key,'cipher_sign':a,'feedback_sign':b,'constant':c,
        'ciphertext_indices':encrypt(plain,key,a,b,c)}


def run(kind,index):
    tick=time.perf_counter();deadline=tick+180
    model,rows,training=models();source=control_source(rows,index)
    if kind=='null':
        original=source['ciphertext_indices'];rng=random.Random(3302075)
        doublets=lambda x:sum(a==b for a,b in zip(x,x[1:]))
        for proposals in range(1,100001):
            if time.perf_counter()>deadline:raise TimeoutError('Null deadline')
            middle=original[1:-1];rng.shuffle(middle);sample=original[:1]+middle+original[-1:]
            if doublets(sample)==doublets(original):break
        else:raise RuntimeError('Null proposal cap')
        source={'ciphertext_indices':sample,'proposals':proposals,'source_control':5}
    probe=None if kind=='null' else [source[k] for k in ('cipher_sign','feedback_sign','constant')]
    result=search(source['ciphertext_indices'],dense_tables(model),deadline,probe)
    out={'experiment':f'E075-{kind}-{index}','kind':kind,'index':index,'parameters':load(PLAN),
        'source':source,'training':training,'result':result,'new_decryptions':[]}
    if kind=='control':
        top=result['top'][0];r=top['recipe']
        out['exact']=top['plaintext_runes']==source['truth_runes']
        out['injected_recipe_exact']=all(r[k]==source[s] for k,s in [('key_indices','injected_key'),('cipher_sign','cipher_sign'),('feedback_sign','feedback_sign'),('constant','constant')])
        out['injected_family_rank']=result['screen_audit']['probe']['rank']
        out['injected_family_retained']=out['injected_family_rank']<=16
        out['correct_runes']=sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
    out['wall_seconds']=time.perf_counter()-tick
    return out


DEPS=BENCH_DEPS+OLD_DEPS+['experiments/delay_three_controls.py','scripts/run_delay_three_controls.py',
    'checkpoints/phase27_benchmark_complete.json']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['control','null']);p.add_argument('index',type=int);args=p.parse_args()
    assert 0<=args.index<16 and (args.kind!='null' or args.index==5)
    bench=load('checkpoints/phase27_benchmark_complete.json');assert bench['gate_passed'] and load(bench['output'])['gate_passed']
    registered(f'E075-{args.kind}-{args.index}',load(PLAN)|vars(args)|{'numpy':np.__version__},DEPS+[bench['output']],lambda:run(args.kind,args.index))
