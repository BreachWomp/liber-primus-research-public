"""E080 fixed word-end model diagnostic, with no unknown-page access."""
import random
import time
import numpy as np
from attack_support import load,to_indices
from heldout_language import corpus,make_models
from substitution_prototype import SWAPS,AUDIT
from terminated_word_arrays import TerminatedArrays
from liberprimus.terminated_words import TerminatedWords
from registry import registered

PLAN='experiments/terminated_substitution_plan.json'


def models():
    rows=corpus();old,_,metadata=make_models(rows)
    train=load('experiments/fragment_benchmark_plan.json')['training_chapters']
    model=TerminatedWords([w for r in rows if r['chapter'] in train for w in r['words']])
    return model,TerminatedArrays(model),old,rows,metadata


def run():
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    model,arrays,old,external,metadata=models()
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    layouts={r['fixture']:r['segment_ends'] for r in load(AUDIT)['controls']}
    previous={r['fixture']:r for r in load('results/E036-boundary-substitution-controls-55de620ad811.json')['controls']}
    error=0.;comparisons=0
    def score(samples,ends):
        nonlocal error,comparisons
        if time.perf_counter()>deadline:raise TimeoutError('E080 deadline')
        direct=[model.score(p,ends) for p in samples];batch=arrays.score(np.array(samples),ends)
        error=max(error,float(np.max(np.abs(batch-np.array(direct)))));comparisons+=len(samples)
        return direct
    controls=[]
    for ident in plan['regressions']:
        plain=to_indices(fixtures[ident]['plaintext_runes']);ends=layouts[ident]
        neighbors=[]
        for a,b in SWAPS.tolist():neighbors.append([b if x==a else a if x==b else x for x in plain])
        scores=score([plain]+neighbors,ends);wrong=to_indices(previous[ident]['result']['top']['plaintext_runes'])
        best=max((s for p,s in zip(neighbors,scores[1:]) if p!=plain),default=-float('inf'))
        controls.append({'fixture':ident,'truth':plain,'segment_ends':ends,'truth_score':scores[0],
            'swaps':SWAPS.tolist(),'neighbor_scores':scores[1:],'best_distinct_neighbor_score':best,
            'strict_local_gate':scores[0]>best+1e-12,'previous_selected_plaintext':wrong,
            'previous_selected_new_score':model.score(wrong,ends),'previous_selected_old_score':old.score(wrong,ends)})
    rng=random.Random(3304080);heldout=[]
    for chapter in ('X','XI','XII'):
        for r in [r for r in external if r['chapter']==chapter and len(r['words'])>=20][:6]:
            values=[];ends=[]
            for word in r['words'][:20]:values.extend(word);ends.append(len(values))
            mutations=[];samples=[values]
            for _ in range(20):
                pos=rng.randrange(len(values));replacement=(values[pos]+rng.randrange(1,29))%29
                p=values[:];p[pos]=replacement;samples.append(p)
                mutations.append({'position':pos,'replacement':replacement})
            new=score(samples,ends);baseline=[old.score(p,ends) for p in samples]
            null=[]
            for k in range(19):
                p=values[:];random.Random(3302080+100*len(heldout)+k).shuffle(p);null.append(p)
            null_new=score(null,ends);null_old=[old.score(p,ends) for p in null]
            heldout.append({'chapter':chapter,'paragraph':r['paragraph'],'source_character_range':r['source_character_range'],
                'values':values,'segment_ends':ends,'mutations':mutations,'new_scores':new,'old_scores':baseline,
                'null_ciphertexts':null,'null_new_scores':null_new,'null_old_scores':null_old})
    wins=[sum(r[k][0]>s+1e-12 for r in heldout for s in r[k][1:]) for k in ('new_scores','old_scores')]
    gates={'local_truth_all':all(r['strict_local_gate'] for r in controls),'mutation_rate':wins[0]/360>=.95,
        'no_loss_over_old':(wins[0]-wins[1])/360>=-.01,'arithmetic':error<1e-9}
    return {'experiment':'E080','parameters':plan,'training':metadata,'controls':controls,'heldout':heldout,
        'new_old_strict_wins':wins,'mutation_comparisons':360,'scalar_vector_comparisons':comparisons,
        'maximum_absolute_error':error,'gates':gates,'gate_passed':all(gates.values()),
        'wall_seconds':time.perf_counter()-tick,'unknown_pages_searched':0,'new_decryptions':[]}


DEPS=[PLAN,'experiments/terminated_benchmark.py','experiments/terminated_word_arrays.py',
    'src/liberprimus/terminated_words.py','experiments/heldout_language.py','experiments/fragment_benchmark_plan.json',
    'src/liberprimus/word_model.py','src/liberprimus/boundaries.py','src/liberprimus/decoding.py',
    'src/liberprimus/alphabet.py','experiments/substitution_prototype.py','src/liberprimus/substitution_patterns.py',
    'src/liberprimus/known_plaintext.py','experiments/external_language.py','experiments/ngram_arrays.py',
    'experiments/attack_support.py','src/liberprimus/ciphers.py',AUDIT,'known_solutions/fixtures.json',
    'results/E036-boundary-substitution-controls-55de620ad811.json',
    'data/raw/gutenberg/pg2944.txt','sources/emerson_manifest.json',
    'scripts/terminated_supervisor.py','scripts/run_terminated_benchmark.py']
if __name__=='__main__':registered('E080-terminated-benchmark',load(PLAN)|{'numpy':np.__version__},DEPS,run)
