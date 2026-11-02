"""External selective-skip injection gate for the unchanged E040 solver."""
import random
import time
import numpy as np
from attack_support import load,to_runes
from periodic_key_controls import models
from joint_skip_controls import DEPS as JOINT_DEPS
from joint_skip_search import search
from liberprimus.periodic_key import encrypt
from ngram_arrays import dense_tables
from conditional_attack_null import conditional_shuffle
from registry import registered

PLAN='experiments/joint_skip_external_plan.json'
HISTORICAL='results/E040-joint-key-skip-controls-17a783e45d76.json'


def run():
    tick=time.perf_counter();deadline=tick+180
    assert load(HISTORICAL)['gate_passed']
    model,external,training=models();lookup=dense_tables(model)
    rng=random.Random(3301041);controls=[]
    for chapter in ('X','XI','XII'):
        eligible=[]
        for row in external:
            if row['chapter']!=chapter:continue
            values=[x for word in row['words'] for x in word]
            if len(values)>=350 and values[:350].count(0)>=2:eligible.append((row,values[:350]))
        assert len(eligible)>=2
        for j,(row,plain) in enumerate(eligible[:2]):
            key=[rng.randrange(1,29) for _ in range((5,13)[j])];sign=(1,-1)[j]
            skips=[i for i,x in enumerate(plain) if x==0][::2]
            cipher=encrypt(plain,key,sign,skips);result=search(cipher,model,lookup,deadline)
            top=result['top'][0]
            checks={'plaintext_exact':top['plaintext_runes']==to_runes(plain),
                    'key_exact':top['key']==key and top['sign']==sign,
                    'mask_exact':top['skip_positions']==skips}
            controls.append({'chapter':chapter,'paragraph':row['paragraph'],'source_character_range':row['source_character_range'],
                'truth_runes':to_runes(plain),'injected_key':key,'injected_sign':sign,'injected_skips':skips,
                'ciphertext_indices':cipher,'result':result,'checks':checks,'exact':all(checks.values())})
            print({'chapter':chapter,'period':len(key),'checks':checks,'seconds':time.perf_counter()-tick},flush=True)
    nulls=[]
    for k in range(3):
        sample,proposals=conditional_shuffle(controls[0]['ciphertext_indices'],random.Random(3302041+k),deadline=deadline)
        nulls.append({'replicate':k,'ciphertext_indices':sample,'proposals':proposals,
                      'result':search(sample,model,lookup,deadline)})
    return {'experiment':'E041-joint-key-skip-external','parameters':load(PLAN),'training':training,
            'controls':controls,'nulls':nulls,'gate_passed':all(r['exact'] for r in controls),
            'unknown_pages_searched':0,'new_decryptions':[],'wall_seconds':time.perf_counter()-tick}


DEPS=JOINT_DEPS+[PLAN,'experiments/joint_skip_external.py',HISTORICAL]
if __name__=='__main__':registered('E041-joint-key-skip-external',load(PLAN)|{'numpy':np.__version__},DEPS,run)
