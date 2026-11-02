"""Registered oracle historical and source-excluded synthetic controls."""
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,digest
from heldout_language import corpus
from liberprimus.decoding import BackoffModel
from liberprimus.periodic_key import encrypt
from ngram_arrays import dense_tables
from periodic_key_search import search
from conditional_attack_null import conditional_shuffle
from registry import registered

PLAN='experiments/periodic_key_plan.json'


def models():
    rows=corpus();chapters=load('experiments/fragment_benchmark_plan.json')['training_chapters']
    train=[r for r in rows if r['chapter'] in chapters]
    sequences=[[x for w in r['words'] for x in w] for r in train]
    return BackoffModel(sequences,order=4,alpha=.5,strength=5),rows,{
        'training_chapters':chapters,'training_source_ranges':[r['source_character_range'] for r in train],
        'training_runes':sum(map(len,sequences)),'source_sha256':digest('data/raw/gutenberg/pg2944.txt')}


def run():
    tick=time.perf_counter();deadline=tick+180;model,external,metadata=models();lookup=dense_tables(model)
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};controls=[]
    for ident in ('LP1-03_04_divinity','LP1-14_15_circumference'):
        f=fixtures[ident];cipher=to_indices(f['ciphertext_runes'])
        found=search(cipher,lookup,deadline,oracle_skips=f['skip_positions'])
        controls.append({'kind':'historical_oracle_skips','fixture':ident,'ciphertext_indices':cipher,
            'truth_runes':f['plaintext_runes'],'oracle_skips':f['skip_positions'],'result':found,
            'exact':found['top'][0]['plaintext_runes']==f['plaintext_runes']})
        print({'control':ident,'exact':controls[-1]['exact'],'seconds':time.perf_counter()-tick},flush=True)
    rng=random.Random(3301038);synthetic=[]
    for chapter in ('X','XI','XII'):
        selected=[r for r in external if r['chapter']==chapter and sum(map(len,r['words']))>=200][:2]
        for j,row in enumerate(selected):
            plain=[x for word in row['words'] for x in word][:200];period=(5,13)[j];sign=(1,-1)[j]
            key=[rng.randrange(29) for _ in range(period)];cipher=encrypt(plain,key,sign)
            found=search(cipher,lookup,deadline)
            record={'kind':'external_synthetic','chapter':chapter,'paragraph':row['paragraph'],
                'source_character_range':row['source_character_range'],'ciphertext_indices':cipher,
                'truth_runes':to_runes(plain),'injected_key':key,'injected_sign':sign,'result':found,
                'exact':found['top'][0]['plaintext_runes']==to_runes(plain)}
            synthetic.append(record);controls.append(record)
            print({'control':chapter,'period':period,'exact':record['exact'],'seconds':time.perf_counter()-tick},flush=True)
    nulls=[]
    for k in range(3):
        cipher,proposals=conditional_shuffle(synthetic[0]['ciphertext_indices'],random.Random(3302038+k),deadline=deadline)
        nulls.append({'replicate':k,'ciphertext_indices':cipher,'proposals':proposals,
                      'result':search(cipher,lookup,deadline)})
    assert len(controls)==8
    return {'experiment':'E038-periodic-key-controls','parameters':load(PLAN),'training':metadata,
            'controls':controls,'nulls':nulls,'gate_passed':all(r['exact'] for r in controls),
            'unknown_pages_searched':0,'new_decryptions':[],'wall_seconds':time.perf_counter()-tick}


DEPS=[PLAN,'experiments/periodic_key_controls.py','experiments/periodic_key_search.py',
      'src/liberprimus/periodic_key.py','experiments/heldout_language.py','experiments/fragment_benchmark_plan.json',
      'experiments/attack_support.py','experiments/ngram_arrays.py','experiments/conditional_attack_null.py',
      'src/liberprimus/alphabet.py','src/liberprimus/ciphers.py','src/liberprimus/decoding.py',
      'src/liberprimus/word_model.py','src/liberprimus/boundaries.py',
      'data/raw/gutenberg/pg2944.txt','sources/emerson_manifest.json','known_solutions/fixtures.json']

if __name__=='__main__':registered('E038-periodic-key-controls',load(PLAN)|{'numpy':np.__version__},DEPS,run)
