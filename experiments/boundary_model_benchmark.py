"""Fixed boundary scoring benchmark; no optimization on unknown candidates."""
import random
import time
from attack_support import load,to_indices,stream_catalog,candidate
from registry import registered
from external_language import paragraphs,external_model
from liberprimus.word_model import WordModel,word_selective_decode

AUDIT='results/E026-boundary-audit-314198a84563.json'

def make_model():
    _,counts,metadata=paragraphs()
    return WordModel(counts,external_model(4),tau=20),metadata

def run():
    tick=time.perf_counter();deadline=tick+180;rng=random.Random(3301027)
    model,source=make_model();rows=[];controls=[]
    layouts={c['fixture']:c['segment_ends'] for c in load(AUDIT)['controls']}
    for f in load('known_solutions/fixtures.json'):
        if not f['canonical_pages_match']:continue
        plain=to_indices(f['plaintext_runes']);ends=layouts[f['id']]
        truth=model.score(plain,ends);baseline=model.character_model.score(plain);mutations=[]
        for width in (1,5):
            for _ in range(100):
                sample=list(plain);start=rng.randrange(len(plain)-width+1)
                for i in range(start,start+width):sample[i]=(sample[i]+rng.randrange(1,29))%29
                mutations.append({'width':width,'start':start,'replacement':sample[start:start+width],
                    'word_score':model.score(sample,ends),'baseline_score':model.character_model.score(sample)})
        rows.append({'fixture':f['id'],'segment_ends':ends,'truth_word_score':truth,'truth_baseline_score':baseline,
            'word_wins':sum(truth>m['word_score'] for m in mutations),
            'baseline_wins':sum(baseline>m['baseline_score'] for m in mutations),'mutations':mutations})
        if f['cipher']=='vigenere':key=f['key_indices'];repeat=True;starts=range(len(key));family='vigenere'
        elif f['id']=='LP2-56_totient_primes':key=stream_catalog(len(plain)+256)['prime_totient'];repeat=False;starts=range(256);family='prime_totient'
        else:continue
        values=to_indices(f['ciphertext_runes'])
        out=word_selective_decode(values,ends,key,model,repeating=repeat,starts=starts,deadline=deadline)
        saved=candidate(out,values,key,{'family':family,'key_indices':key if repeat else None,'cipher_sign':1,'key_sign':-1},repeat)
        saved.update(fixture=f['id'],exact=out.plaintext==plain,segment_ends=ends,expected_skips=f['skip_positions'])
        controls.append(saved)
        print({'control':f['id'],'exact':saved['exact'],'seconds':time.perf_counter()-tick},flush=True)
    wins=sum(row['word_wins'] for row in rows);baseline=sum(row['baseline_wins'] for row in rows)
    assert time.perf_counter()<deadline
    return {'experiment':'E027-boundary-model-benchmark','status':'completed','source':source,
        'parameters':load('experiments/boundary_model_plan.json'),'rows':rows,'controls':controls,
        'word_strict_wins':wins,'baseline_strict_wins':baseline,'comparisons':1600,
        'gate_passed':len(controls)==3 and all(c['exact'] for c in controls) and wins>=1520,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}

DEPS=['experiments/boundary_model_benchmark.py','experiments/boundary_model_plan.json',AUDIT,
    'src/liberprimus/word_model.py','src/liberprimus/boundaries.py','src/liberprimus/alphabet.py',
    'src/liberprimus/decoding.py','src/liberprimus/ciphers.py','experiments/attack_support.py',
    'experiments/external_language.py','experiments/external_model_plan.json','known_solutions/fixtures.json',
    'data/raw/gutenberg/pg2944.txt','sources/emerson_manifest.json','sources/boundary_image_manifest.json',
    'sources/boundary_layout_decisions.json','sources/LP2-35-boundary-crop.png',
    'data/raw/scream314/assets/2014/liber-primus-complete/52.jpg']

if __name__=='__main__':
    registered('E027-boundary-model',{'seconds':180,'seed':3301027,'tau':20},DEPS,run)
