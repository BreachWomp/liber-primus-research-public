"""Raw-source event recount and separate scalar probability calculation for E080."""
from collections import Counter,defaultdict
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path
import random
import sys
import time
import hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments')]
from heldout_language import corpus,tokenize,make_models
from attack_support import to_indices

def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


class Reference:
    def __init__(self):
        self.rows=corpus();self.old,_,self.training=make_models(self.rows)
        self.raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
        assert sha('data/raw/gutenberg/pg2944.txt')==load('sources/emerson_manifest.json')['sha256']
        train=load('experiments/fragment_benchmark_plan.json')['training_chapters']
        expected=[r['source_character_range'] for r in self.rows if r['chapter'] in train]
        assert self.training['training_source_ranges']==expected
        words=[]
        for a,b in expected:words.extend(tokenize(self.raw[a:b])[0])
        self.words=Counter(words);self.events=defaultdict(Counter)
        # Literal padded token events, rather than the production rolling history.
        for w in words:
            padded=[29,29,29]+list(w)+[30]
            for i in range(3,len(padded)):
                for order in range(4):self.events[tuple(padded[i-order:i])][padded[i]]+=1
        self.totals={h:sum(c.values()) for h,c in self.events.items()};self.n=len(words)

    @lru_cache(maxsize=100000)
    def probability(self,h,x):
        if not h:return (self.events[()].get(x,0)+.5)/(self.totals[()]+15)
        low=self.probability(h[1:],x)
        return (self.events.get(h,{}).get(x,0)+5*low)/(self.totals.get(h,0)+5)

    @lru_cache(maxsize=100000)
    def word(self,w):
        padded=(29,29,29)+w+(30,)
        q=math.prod(self.probability(padded[i-3:i],padded[i]) for i in range(3,len(padded)))
        return math.log((self.words.get(w,0)+20*q)/(self.n+20))

    def score(self,p,ends):
        start=0;total=0
        for end in ends:total+=self.word(tuple(p[start:end]));start=end
        assert start==len(p)
        return total/len(p)

    def source_window(self,row,count):
        source=next(r for r in self.rows if r['chapter']==row['chapter'] and r['paragraph']==row['paragraph'])
        a,b=source['source_character_range'];assert row['source_character_range']==[a,b]
        words=tokenize(self.raw[a:b])[0][:count];values=[];ends=[]
        for word in words:values+=word;ends.append(len(values))
        return values,ends


def main():
    tick=time.perf_counter();v=Reference();path=load('checkpoints/phase29_benchmark_complete.json')['output'];row=load(path)
    e=next(e for e in map(json.loads,(ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()) if e['status']=='completed' and e['output']==path)
    assert sha(path)==e['output_sha256']
    for p,h in e['input_dependencies'].items():assert sha(p)==h,p
    assert row['parameters']==load('experiments/terminated_substitution_plan.json') and row['training']==v.training
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    audit=load('results/E026-boundary-audit-314198a84563.json')
    layouts={r['fixture']:r['segment_ends'] for r in audit['controls']}
    checks=0;error=0.
    def check(p,ends,s):
        nonlocal checks,error
        assert time.perf_counter()-tick<180
        error=max(error,abs(v.score(p,ends)-s));checks+=1;assert error<1e-9
    local=[]
    for r in row['controls']:
        p=to_indices(fixtures[r['fixture']]['plaintext_runes']);ends=layouts[r['fixture']]
        assert r['truth']==p and r['segment_ends']==ends
        check(p,ends,r['truth_score']);assert r['swaps']==[list(x) for x in itertools.combinations(range(29),2)]
        distinct=[]
        for (a,b),score in zip(r['swaps'],r['neighbor_scores']):
            q=[{a:b,b:a}.get(x,x) for x in p];check(q,ends,score)
            if q!=p:distinct.append(score)
        assert max(distinct)==r['best_distinct_neighbor_score']
        gate=r['truth_score']>max(distinct)+1e-12;assert gate==r['strict_local_gate'];local.append(gate)
        old=next(x for x in load('results/E036-boundary-substitution-controls-55de620ad811.json')['controls'] if x['fixture']==r['fixture'])
        q=to_indices(old['result']['top']['plaintext_runes']);assert q==r['previous_selected_plaintext']
        check(q,ends,r['previous_selected_new_score']);assert abs(v.old.score(q,ends)-r['previous_selected_old_score'])<1e-9
    eligible=[r for ch in ('X','XI','XII') for r in [r for r in v.rows if r['chapter']==ch and len(r['words'])>=20][:6]]
    assert [(r['chapter'],r['paragraph']) for r in row['heldout']]==[(r['chapter'],r['paragraph']) for r in eligible]
    rng=random.Random(3304080);wins=[0,0];null_wins=[0,0]
    for index,r in enumerate(row['heldout']):
        p,ends=v.source_window(r,20);assert r['values']==p and r['segment_ends']==ends
        samples=[p]
        for m in r['mutations']:
            pos=rng.randrange(len(p));x=(p[pos]+rng.randrange(1,29))%29
            assert m=={'position':pos,'replacement':x};q=p[:];q[pos]=x;samples.append(q)
        for q,new,old in zip(samples,r['new_scores'],r['old_scores']):
            check(q,ends,new);assert abs(v.old.score(q,ends)-old)<1e-9
        for j,k in enumerate(('new_scores','old_scores')):wins[j]+=sum(r[k][0]>s+1e-12 for s in r[k][1:])
        for k,(q,new,old) in enumerate(zip(r['null_ciphertexts'],r['null_new_scores'],r['null_old_scores'])):
            expected=p[:];random.Random(3302080+100*index+k).shuffle(expected);assert q==expected
            check(q,ends,new);assert abs(v.old.score(q,ends)-old)<1e-9
            null_wins[0]+=r['new_scores'][0]>new;null_wins[1]+=r['old_scores'][0]>old
    gates={'local_truth_all':all(local),'mutation_rate':wins[0]/360>=.95,'no_loss_over_old':(wins[0]-wins[1])/360>=-.01,'arithmetic':row['maximum_absolute_error']<1e-9}
    assert gates==row['gates'] and row['gate_passed']==all(gates.values()) and wins==row['new_old_strict_wins']
    result={'gate_passed':row['gate_passed'],'output':path,'sha256':sha(path),'fingerprint':e['fingerprint'],
        'independent_scores':checks,'max_absolute_error':error,'new_old_mutation_wins':wins,'new_old_null_wins':null_wins,
        'validation_seconds':time.perf_counter()-tick,'verifier_sha256':sha('scripts/verify_terminated_benchmark.py'),
        'source_note':'Raw bytes and training ranges verified; declared GP tokenizer shared, event counts/probability/scoring implementation separate.'}
    (ROOT/'results/phase29_benchmark_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(result)


if __name__=='__main__':main()
