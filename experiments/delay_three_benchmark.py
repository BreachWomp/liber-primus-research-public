"""E074 registered mathematical validation and throughput, no unknown text."""
import random
import time
import numpy as np
from attack_support import load
from periodic_key_controls import models,DEPS as BASE_DEPS
from ngram_arrays import dense_tables
from delay_three_search import PREFIXES,prefix_scores,search
from registry import registered
PLAN='experiments/delay_three_plan.json'


def run():
    tick=time.perf_counter();deadline=tick+180
    rng=random.Random(3301074);cipher=[rng.randrange(29) for _ in range(13)]
    nrng=np.random.default_rng(3301074);lookup=[nrng.normal(size=(29,)*k) for k in range(1,5)]
    checks=0;error=0.0
    for a,b,c in ((7,1,19),(14,28,0),(2,15,9)):
        actual=prefix_scores(cipher,a,b,c,lookup,deadline)
        for index,prefix in enumerate(PREFIXES.tolist()):
            if index%1024==0 and time.perf_counter()>deadline:raise TimeoutError('Scalar audit deadline')
            plain=prefix[:]
            for i in range(3,len(cipher)):plain.append((a*cipher[i]+b*plain[i-3]+c)%29)
            total=sum(float(lookup[min(i,3)][tuple(plain[max(0,i-3):i+1])]) for i in range(len(cipher)))/len(cipher)
            error=max(error,abs(total-actual[index]));checks+=1
    assert error<1e-9
    model,_,training=models();rng=random.Random(3302074)
    cipher=[rng.randrange(29) for _ in range(3316)]
    start=time.perf_counter();result=search(cipher,dense_tables(model),deadline)
    elapsed=time.perf_counter()-start
    return {'experiment':'E074','parameters':load(PLAN),'literal_prefix_comparisons':checks,
        'max_absolute_error':float(error),'benchmark_seconds':elapsed,'benchmark_runes':3316,
        'training':training,'ciphertext_indices':cipher,'result':result,'gate_passed':elapsed<120,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


DEPS=BASE_DEPS+[PLAN,'experiments/delay_three_benchmark.py','experiments/delay_three_search.py',
    'experiments/affine_feedback_factors.py','src/liberprimus/affine_feedback.py','src/liberprimus/bilinear_feedback.py',
    'scripts/run_delay_three_benchmark.py','scripts/delay_three_supervisor.py']
if __name__=='__main__':registered('E074-benchmark',load(PLAN)|{'numpy':np.__version__},DEPS,run)
