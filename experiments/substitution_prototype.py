"""Word-pattern seeded, bounded general monoalphabetic substitution prototype."""
from collections import Counter,defaultdict
import itertools
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes
from external_language import paragraphs,external_model
from ngram_arrays import dense_tables,array_scores
from liberprimus.alphabet import transliterate
from liberprimus.boundaries import segments
from liberprimus.known_plaintext import substitution_constraints
from liberprimus.substitution_patterns import equality_pattern,complete_mapping
from registry import registered

PLAN='experiments/substitution_prototype_plan.json'
AUDIT='results/E026-boundary-audit-314198a84563.json'
SWAPS=np.array(list(itertools.combinations(range(29),2)),dtype=np.int32)


def starts(values,ends,counts,seed):
    buckets=defaultdict(list)
    for word,count in counts.items():buckets[equality_pattern(word)].append((count,word))
    for bucket in buckets.values():bucket.sort(key=lambda row:(-row[0],row[1]))
    cipher_counts=Counter(values);plain_counts=Counter()
    for word,count in counts.items():
        for symbol in word:plain_counts[symbol]+=count
    options=[];seen=set();offset=0
    for word in segments(values,ends):
        token=tuple(word);bucket=buckets.get(equality_pattern(word),[])
        if token not in seen and 4<=len(word)<=14 and bucket:
            options.append((len(bucket),-len(word),offset,token,bucket))
        seen.add(token);offset+=len(word)
    initial=[];anchors=[]
    for _,_,offset,word,bucket in sorted(options)[:4]:
        for count,target in bucket[:4]:
            partial=substitution_constraints(word,target);assert partial is not None
            initial.append(complete_mapping(partial,cipher_counts,plain_counts))
            anchors.append({'offset':offset,'cipher_word':list(word),'target_word':list(target),'frequency':count})
    base=complete_mapping({},cipher_counts,plain_counts);initial.append(base);rng=random.Random(seed)
    for _ in range(7):
        row=list(base)
        for _ in range(8):
            a,b=rng.sample(range(29),2);row[a],row[b]=row[b],row[a]
        initial.append(tuple(row))
    return list(dict.fromkeys(initial)),anchors


def solve(values,ends,counts,lookup,seed,deadline):
    if not 1<=len(values)<=1024:raise ValueError('Cipher length outside bound')
    initial,anchors=starts(values,ends,counts,seed);assert len(initial)<=24
    cipher=np.array(values,dtype=np.int32);records=[];best=None
    for number,key in enumerate(initial):
        key=np.array(key,dtype=np.int32)
        score=float(array_scores(key[cipher][None,:],lookup)[0]);evaluations=1;steps=0
        for _ in range(40):
            if time.perf_counter()>deadline:raise TimeoutError('E035 deadline')
            neighbors=np.tile(key,(len(SWAPS),1));idx=np.arange(len(SWAPS))
            neighbors[idx,SWAPS[:,0]]=key[SWAPS[:,1]];neighbors[idx,SWAPS[:,1]]=key[SWAPS[:,0]]
            scores=array_scores(neighbors[:,cipher],lookup);evaluations+=len(SWAPS)
            chosen=int(scores.argmax());candidate_score=float(scores[chosen])
            if candidate_score<=score+1e-12:break
            key=neighbors[chosen].copy();score=candidate_score;steps+=1
        plain=key[cipher].tolist();mapping=key.tolist()
        row={'restart':number,'score':score,'mapping_cipher_to_plain':mapping,'plaintext_runes':to_runes(plain),
             'transliteration':transliterate(plain),'accepted_swaps':steps,'evaluations':evaluations}
        records.append(row)
        if best is None or score>best['score']:best=row
    return {'top':best,'restarts':records,'anchors':anchors,'evaluations':sum(r['evaluations'] for r in records)}


def run():
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN)
    _,counts,metadata=paragraphs();lookup=dense_tables(external_model(4))
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    layouts={r['fixture']:r['segment_ends'] for r in load(AUDIT)['controls']}
    rng=random.Random(plan['seed']);rows=[]
    for j,ident in enumerate(plan['controls']):
        f=fixtures[ident];plain=to_indices(f['plaintext_runes']);ends=layouts[ident]
        permutation=list(range(29));rng.shuffle(permutation);cipher=[permutation[x] for x in plain]
        seed=3303035+100*j;solved=solve(cipher,ends,counts,lookup,seed,deadline)
        actual=to_indices(solved['top']['plaintext_runes']);nulls=[]
        for k in range(3):
            shuffled=cipher[:];random.Random(3302035+100*j+k).shuffle(shuffled);proposals=1
            result=solve(shuffled,ends,counts,lookup,seed,deadline)
            nulls.append({'replicate':k,'ciphertext_indices':shuffled,'proposals':proposals,'result':result})
        words=segments(plain,ends)
        rows.append({'fixture':ident,'permutation_plain_to_cipher':permutation,'ciphertext_indices':cipher,
            'segment_ends':ends,'search_seed':seed,'result':solved,'exact':actual==plain,
            'correct_positions':sum(a==b for a,b in zip(actual,plain)),'runes':len(plain),
            'dictionary_word_tokens':sum(tuple(w) in counts for w in words),'word_tokens':len(words),'nulls':nulls})
        print({'control':ident,'exact':rows[-1]['exact'],'correct':rows[-1]['correct_positions'],
               'runes':len(plain),'seconds':time.perf_counter()-tick},flush=True)
    assert time.perf_counter()<deadline
    return {'experiment':'E035-substitution-prototype','parameters':plan,'external_source':metadata,'controls':rows,
        'gate_passed':all(r['exact'] for r in rows),'unknown_pages_searched':0,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


DEPS=['experiments/substitution_prototype.py',PLAN,AUDIT,'src/liberprimus/substitution_patterns.py',
      'src/liberprimus/known_plaintext.py','src/liberprimus/boundaries.py','src/liberprimus/alphabet.py',
      'src/liberprimus/decoding.py','src/liberprimus/ciphers.py','experiments/external_language.py',
      'experiments/external_model_plan.json','experiments/ngram_arrays.py','experiments/attack_support.py',
      'experiments/conditional_attack_null.py','data/raw/gutenberg/pg2944.txt','sources/emerson_manifest.json',
      'known_solutions/fixtures.json']

if __name__=='__main__':registered('E035-substitution-prototype',load(PLAN)|{'numpy':np.__version__},DEPS,run)
