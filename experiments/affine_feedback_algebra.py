"""E071 independent direct queue enumeration; no cryptanalytic claims."""
import random
import time
import numpy as np
from attack_support import load
from registry import registered
from affine_feedback_factors import period_scores, screen
PLAN='experiments/affine_feedback_algebra_plan.json'


def literal(values,m,a,b,c,logp):
    # One independent queue for every possible repeated prefix symbol.
    rows=np.empty((29,len(values)),dtype=np.int16)
    rows[:,:m]=np.arange(29)[:,None]
    for i in range(m,len(values)):
        rows[:,i]=(a*values[i]+b*rows[:,i-m]+c)%29
    return sum(logp[rows[:,r::m]].sum(axis=1).max() for r in range(m))


def run():
    tick=time.perf_counter();deadline=tick+120
    logp=np.log(np.arange(1,30)/435);rng=random.Random(3301071)
    comparisons=0;error=0.0
    for m,n,units in ((4,41,range(1,29)),(13,101,(1,7,28)),(32,101,(1,7,28))):
        values=[rng.randrange(29) for _ in range(n)]
        scores=period_scores(values,m,logp,deadline)
        for a in units:
            for b in range(1,29):
                if time.perf_counter()>deadline:raise TimeoutError('Direct audit deadline')
                for c in range(29):
                    error=max(error,abs(literal(values,m,a,b,c,logp)-scores[a-1,b-1,c]));comparisons+=1
    assert error<1e-7
    rng=random.Random(3302071);values=[rng.randrange(29) for _ in range(3316)]
    start=time.perf_counter();retained,audit=screen(values,logp,deadline)
    elapsed=time.perf_counter()-start
    return {'experiment':'E071','direct_families_checked':comparisons,'max_absolute_error':float(error),
        'benchmark_seconds':elapsed,'benchmark_runes':3316,'screened_families':29*22736,
        'retained_families':len(retained),'audit':audit,'gate_passed':elapsed<60,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


DEPS=[PLAN,'experiments/affine_feedback_algebra.py','experiments/affine_feedback_factors.py',
    'src/liberprimus/affine_feedback.py','src/liberprimus/bilinear_feedback.py','experiments/attack_support.py']
if __name__=='__main__':
    registered('E071-algebra',load(PLAN)|{'numpy':np.__version__},DEPS,run)
