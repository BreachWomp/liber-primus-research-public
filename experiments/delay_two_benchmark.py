"""E077 registered mathematical validation and throughput, no unknown text."""
import random
import time
import itertools
import numpy as np
from attack_support import load
from periodic_key_controls import models,DEPS as BASE_DEPS
from ngram_arrays import dense_tables
from delay_two_search import PREFIXES,prefix_scores,search
from registry import registered
PLAN='experiments/delay_two_plan.json'


def run():
    tick=time.perf_counter();deadline=tick+180
    rng=random.Random(3301077);cipher=[rng.randrange(29) for _ in range(13)]
    nrng=np.random.default_rng(3301077);lookup=[nrng.normal(size=(29,)*k) for k in range(1,5)]
    checks=0;error=0.0
    for a,b,c in ((7,1,19),(14,28,0),(2,15,9)):
        actual=prefix_scores(cipher,a,b,c,lookup,deadline)
        for index,prefix in enumerate(PREFIXES.tolist()):
            if index%1024==0 and time.perf_counter()>deadline:raise TimeoutError('Scalar audit deadline')
            plain=prefix[:]
            for i in range(2,len(cipher)):plain.append((a*cipher[i]+b*plain[i-2]+c)%29)
            total=sum(float(lookup[min(i,3)][tuple(plain[max(0,i-3):i+1])]) for i in range(len(cipher)))/len(cipher)
            error=max(error,abs(total-actual[index]));checks+=1
    assert error<1e-9
    model,_,training=models();real=dense_tables(model)
    rng=random.Random(3303077);pilot_cipher=[rng.randrange(29) for _ in range(277)]
    start=time.perf_counter();pilot_best=-float('inf')
    for a,b,c in itertools.islice(itertools.product(range(1,29),range(1,29),range(29)),256):
        pilot_best=max(pilot_best,float(prefix_scores(pilot_cipher,a,b,c,real,deadline).max()))
    pilot_seconds=time.perf_counter()-start
    rng=random.Random(3302077)
    cipher=[rng.randrange(29) for _ in range(3316)]
    start=time.perf_counter();result=search(cipher,real,deadline)
    elapsed=time.perf_counter()-start
    return {'experiment':'E077','parameters':load(PLAN),'literal_prefix_comparisons':checks,
        'max_absolute_error':float(error),'benchmark_seconds':elapsed,'benchmark_runes':3316,
        'pilot':{'families':256,'runes':277,'seconds':pilot_seconds,'score':pilot_best,
            'estimated_full_grid_seconds_per_277_rune_input':pilot_seconds*22736/256,
            'estimated_55_equal_length_inputs_seconds':pilot_seconds*22736/256*55,
            'estimate_only_not_full_grid_run':True},
        'training':training,'ciphertext_indices':cipher,'result':result,'gate_passed':elapsed<120,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


DEPS=BASE_DEPS+[PLAN,'experiments/delay_two_benchmark.py','experiments/delay_two_search.py',
    'experiments/affine_feedback_factors.py','src/liberprimus/affine_feedback.py','src/liberprimus/bilinear_feedback.py',
    'scripts/run_delay_two_benchmark.py','scripts/delay_two_supervisor.py']
if __name__=='__main__':registered('E077-benchmark',load(PLAN)|{'numpy':np.__version__},DEPS,run)
