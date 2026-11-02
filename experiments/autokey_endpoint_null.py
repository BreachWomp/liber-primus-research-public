"""Supplemental endpoint-preserving diagnostic, with original mismatch retained."""
import random
import time
import numpy as np
from autokey_extended_controls import DEPS,control_source
from autokey_extended_search import search
from periodic_key_controls import models
from ngram_arrays import dense_tables
from attack_support import load
from registry import registered
PLAN='experiments/autokey_endpoint_null_plan.json'


def run():
    tick=time.perf_counter();deadline=tick+180;model,rows,training=models()
    original=control_source(rows,2)['ciphertext_indices'];rng=random.Random(3302062)
    doublets=lambda a:sum(x==y for x,y in zip(a,a[1:]))
    for proposals in range(1,100001):
        middle=original[1:-1];rng.shuffle(middle);sample=original[:1]+middle+original[-1:]
        if doublets(sample)==doublets(original):break
    else:raise TimeoutError('Null rejection cap')
    result=search(sample,dense_tables(model),deadline)
    return {'experiment':'E062-null-endpoints','kind':'null_endpoints','index':2,'parameters':load(PLAN),'training':training,
        'source':{'ciphertext_indices':sample,'proposals':proposals,'source_control':2},'result':result,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


if __name__=='__main__':
    registered('E062-null-endpoints',load(PLAN)|{'numpy':np.__version__},DEPS+[PLAN,
        'experiments/autokey_endpoint_null.py','scripts/run_autokey_endpoint_null.py'],run)
