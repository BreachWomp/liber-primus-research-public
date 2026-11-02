"""Fixed fresh conditional-null follow-up; no candidate optimization changes."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,ROOT,digest
from affine_plaintext_feedback import search
from external_language import external_model
from ngram_arrays import dense_tables
from conditional_attack_null import conditional_shuffle
from registry import registered


def run(batch,seconds):
    tick=time.perf_counter();deadline=tick+seconds
    plan=load('experiments/affine_confirmation_plan.json')
    assert 0<=batch<plan['batches']
    for path,expected in plan['frozen_inputs'].items():assert digest(path)==expected
    prior=load(plan['initial_null_output']);row=prior['pages'][0]
    canonical=next(p for p in load('transcriptions/pages.json') if p['id']==row['page'])
    assert row['ciphertext_runes']==canonical['runes']
    values=to_indices(row['ciphertext_runes']);observed=row['top'][0]['score']
    assert prior['null_calibration']['monte_carlo_p']==0.05
    rng=random.Random(plan['seed']+batch);lookup=dense_tables(external_model(4));runs=[]
    for i in range(plan['batch_size']):
        sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
        score,_,count=search(sample,lookup,deadline,keep=0)
        runs.append({'index':batch*plan['batch_size']+i,'score':score,'ciphertext_indices':sample,'proposals':proposals,'recipes':count})
    return {'experiment':'E020-affine-feedback-confirmation','status':'completed','batch':batch,
        'parameters':{'seed':plan['seed']+batch,'seconds':seconds,'replicates':plan['batch_size']},
        'page':row['page'],'observed_score':observed,'runs':runs,'exceedances':sum(r['score']>=observed for r in runs),
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[],
        'limits':['Fresh fixed4000-replicate follow-up, no pooling with the trigger19 and no early stop.',
                  'Optimizer and score fixed from E019; page55 and score fixed before follow-up; selection correction55pages x2attack families.']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',type=int,required=True);p.add_argument('--seconds',type=float,default=180.0);args=p.parse_args()
    deps=['experiments/affine_feedback_confirmation.py','experiments/affine_confirmation_plan.json',
        'experiments/affine_plaintext_feedback.py','experiments/affine_feedback_plan.json','experiments/external_language.py',
        'experiments/external_model_plan.json','experiments/ngram_arrays.py','experiments/attack_support.py',
        'experiments/conditional_attack_null.py','src/liberprimus/alphabet.py','src/liberprimus/ciphers.py',
        'src/liberprimus/decoding.py','known_solutions/fixtures.json','transcriptions/pages.json',
        'sources/emerson_manifest.json','data/raw/gutenberg/pg2944.txt']
    deps+=list(load('experiments/affine_confirmation_plan.json')['frozen_inputs'])
    registered(f'E020-null-batch-{args.batch:02}',{**vars(args),'numpy':np.__version__},deps,lambda:run(args.batch,args.seconds))
