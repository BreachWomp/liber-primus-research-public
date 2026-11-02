"""Pattern-seeded character warmup followed by fixed word-score refinement."""
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from heldout_language import corpus,make_models
from substitution_prototype import solve as warmup,SWAPS,AUDIT
from word_arrays import WordArrays
from liberprimus.alphabet import transliterate
from registry import registered

PLAN='experiments/boundary_substitution_plan.json'


def models():
    rows=corpus();model,_,metadata=make_models(rows)
    return model,WordArrays(model),metadata,rows


def solve(values,ends,model,arrays,seed,deadline):
    first=warmup(values,ends,model.counts,arrays.lookup,seed,deadline)
    cipher=np.array(values,dtype=np.int32);records=[];best=None
    for initial in first['restarts']:
        key=np.array(initial['mapping_cipher_to_plain'],dtype=np.int32)
        score=float(arrays.score(key[cipher][None,:],ends)[0]);evaluations=1;steps=0
        for _ in range(40):
            if time.perf_counter()>deadline:raise TimeoutError('Boundary substitution deadline')
            neighbors=np.tile(key,(len(SWAPS),1));idx=np.arange(len(SWAPS))
            neighbors[idx,SWAPS[:,0]]=key[SWAPS[:,1]];neighbors[idx,SWAPS[:,1]]=key[SWAPS[:,0]]
            scores=arrays.score(neighbors[:,cipher],ends);evaluations+=len(SWAPS)
            chosen=int(scores.argmax());new=float(scores[chosen])
            if new<=score+1e-12:break
            key=neighbors[chosen].copy();score=new;steps+=1
        plain=key[cipher].tolist()
        row={'restart':initial['restart'],'score':score,'mapping_cipher_to_plain':key.tolist(),
             'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain),
             'word_accepted_swaps':steps,'word_evaluations':evaluations}
        records.append(row)
        if best is None or score>best['score']:best=row
    return {'top':best,'restarts':records,'warmup':first,
            'evaluations':first['evaluations']+sum(r['word_evaluations'] for r in records)}


def run():
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN);model,arrays,metadata,external=models()
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    layouts={r['fixture']:r['segment_ends'] for r in load(AUDIT)['controls']}
    rng=random.Random(plan['seed']);controls=[]
    for j,ident in enumerate(plan['controls']):
        plain=to_indices(fixtures[ident]['plaintext_runes']);ends=layouts[ident]
        permutation=list(range(29));rng.shuffle(permutation);cipher=[permutation[x] for x in plain]
        seed=3303036+100*j;result=solve(cipher,ends,model,arrays,seed,deadline);nulls=[]
        for k in range(3):
            sample=cipher[:];random.Random(3302036+100*j+k).shuffle(sample)
            nulls.append({'replicate':k,'ciphertext_indices':sample,
                          'result':solve(sample,ends,model,arrays,seed,deadline)})
        found=to_indices(result['top']['plaintext_runes'])
        controls.append({'fixture':ident,'ciphertext_indices':cipher,'segment_ends':ends,
            'permutation_plain_to_cipher':permutation,'search_seed':seed,'result':result,'nulls':nulls,
            'exact':found==plain,'correct_positions':sum(a==b for a,b in zip(found,plain)),
            'runes':len(plain),'truth_word_score':model.score(plain,ends)})
        print({'control':ident,'exact':found==plain,'correct':controls[-1]['correct_positions'],
               'runes':len(plain),'seconds':time.perf_counter()-tick},flush=True)
    rng=random.Random(3304036);heldout=[]
    for chapter in ('X','XI','XII'):
        eligible=[r for r in external if r['chapter']==chapter and len(r['words'])>=20][:6]
        for r in eligible:
            values=[];ends=[]
            for word in r['words'][:20]:values.extend(word);ends.append(len(values))
            truth=[model.character_model.score(values),model.score(values,ends)];mutations=[]
            for _ in range(20):
                pos=rng.randrange(len(values));replacement=(values[pos]+rng.randrange(1,29))%29
                sample=values[:];sample[pos]=replacement
                mutations.append({'position':pos,'replacement':replacement,
                                  'scores':[model.character_model.score(sample),model.score(sample,ends)]})
            heldout.append({'chapter':chapter,'paragraph':r['paragraph'],'source_character_range':r['source_character_range'],
                            'values':values,'segment_ends':ends,'truth_scores':truth,'mutations':mutations})
    wins=[sum(row['truth_scores'][k]>m['scores'][k]+1e-12 for row in heldout for m in row['mutations']) for k in range(2)]
    comparisons=sum(len(r['mutations']) for r in heldout)
    checks={'all_controls_exact':all(r['exact'] for r in controls),'heldout_word_rate_at_least_095':wins[1]/comparisons>=.95,
            'heldout_loss_at_most_001':(wins[1]-wins[0])/comparisons>=-.01}
    assert time.perf_counter()<deadline
    return {'experiment':'E036-boundary-substitution-controls','parameters':plan,'training':metadata,
        'controls':controls,'heldout':heldout,'heldout_wins_character_word':wins,'heldout_comparisons':comparisons,
        'gate_checks':checks,'gate_passed':all(checks.values()),'wall_seconds':time.perf_counter()-tick,
        'unknown_pages_searched':0,'new_decryptions':[]}


DEPS=['experiments/boundary_substitution.py',PLAN,'experiments/word_arrays.py','experiments/heldout_language.py',
      'experiments/fragment_benchmark_plan.json','experiments/substitution_prototype.py',AUDIT,
      'src/liberprimus/word_model.py','src/liberprimus/substitution_patterns.py','src/liberprimus/known_plaintext.py',
      'src/liberprimus/boundaries.py','src/liberprimus/alphabet.py','src/liberprimus/decoding.py',
      'src/liberprimus/ciphers.py','experiments/attack_support.py','experiments/external_language.py',
      'experiments/ngram_arrays.py','data/raw/gutenberg/pg2944.txt','sources/emerson_manifest.json','known_solutions/fixtures.json']

if __name__=='__main__':registered('E036-boundary-substitution-controls',load(PLAN)|{'numpy':np.__version__},DEPS,run)
