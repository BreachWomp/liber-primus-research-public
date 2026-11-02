"""Independent scalar queue, raw-source and local optimality audit for E062."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments')]
from periodic_key_controls import models
from heldout_language import tokenize,corpus
from ngram_arrays import dense_tables
from attack_support import to_indices
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


class Verifier:
    def __init__(self):
        self.model,self.rows,self.training=models();self.lookup=dense_tables(self.model);self.counts=Counter();self.windows={}

    def decode(self,cipher,prefix,cs,ks):
        key=[(p-cs*c)*ks%29 for p,c in zip(prefix,cipher)];queue=key[:];plain=[]
        for i,c in enumerate(cipher):
            p=(cs*c+ks*queue[i])%29;plain.append(p);queue.append(p)
        self.counts['scalar_decodings']+=1
        return plain,key

    def score(self,plain,order=4):
        return sum(self.model.logp(tuple(plain[max(0,i-order+1):i]),x) for i,x in enumerate(plain))/len(plain)

    def proposals(self,plain,m,ks,residue,order):
        # Independent window enumeration: only windows touching a changed chain.
        ident=(len(plain),m,residue,order)
        if ident not in self.windows:
            affected=sorted({end for p in range(residue,len(plain),m) for end in range(p,min(len(plain),p+order))})
            self.windows[ident]=[np.array([list(range(max(0,e-order+1),e+1)) for e in affected if min(order,e+1)==k],dtype=int).reshape(-1,k) for k in range(1,order+1)]
        result=np.zeros(29)
        for k,positions in enumerate(self.windows[ident],1):
            if not len(positions):continue
            old=np.array(plain)[positions]
            coeff=np.where(positions%m==residue, np.where((positions//m)%2==0,1,ks),0)
            trial=(old[None,:,:]+(np.arange(29)-plain[residue])[:,None,None]*coeff[None,:,:])%29
            result+=self.lookup[k-1][tuple(trial[:,:,j] for j in range(k))].sum(axis=1)
        return result

    def result(self,cipher,result):
        n=len(cipher);expected=[(m,cs,ks) for m in range(4,33) for cs,ks in ((1,-1),(1,1),(-1,-1),(-1,1))]
        assert [(f['period'],f['cipher_sign'],f['feedback_sign']) for f in result['families']]==expected
        pool=[]
        for f in result['families']:
            m,cs,ks=f['period'],f['cipher_sign'],f['feedback_sign'];assert len(f['starts'])==8
            for start in f['starts']:
                initial,_=self.decode(cipher,start['initial'],cs,ks);plain,_=self.decode(cipher,start['prefix'],cs,ks)
                a,b=self.score(initial,3)*n,self.score(plain,3)*n
                assert abs(a-start['initial_total'])<1e-7 and abs(b-start['final_total'])<1e-7
                assert b>=a-1e-7 and 1<=start['sweeps']<=6
                if start['converged']:
                    for r in range(m):
                        scores=self.proposals(plain,m,ks,r,3)
                        assert float(scores.max()-scores[plain[r]])<1e-8
                    self.counts['independent_trigram_coordinate_optima']+=1
                self.counts['initial_and_final_scores']+=2
            for row in f['candidates']:
                assert (row['period'],row['cipher_sign'],row['feedback_sign'])==(m,cs,ks)
                plain,key=self.decode(cipher,row['prefix'],cs,ks)
                assert abs(self.score(plain)-row['score'])<1e-9
                assert abs(self.score(plain,3)-row['trigram_score'])<1e-9
                self.counts['candidate_score_pairs']+=1;pool.append(row)
        selected=[];seen=set()
        for row in sorted(pool,key=lambda x:x['score'],reverse=True):
            ident=(row['period'],row['cipher_sign'],row['feedback_sign'],tuple(row['prefix']))
            if ident not in seen:seen.add(ident);selected.append(row)
            if len(selected)==12:break
        assert [r['initial'] for r in result['refinements']]==selected
        final=[]
        for refinement in result['refinements']:
            r=refinement['initial'];m,cs,ks=r['period'],r['cipher_sign'],r['feedback_sign'];last=r['score']
            assert 1<=len(refinement['trace'])<=6
            for row in refinement['trace']:
                plain,key=self.decode(cipher,row['prefix'],cs,ks);score=self.score(plain)
                assert abs(score-row['score'])<1e-9 and score>=last-1e-9;last=score
                self.counts['fourgram_trace_scores']+=1
            if refinement['converged']:
                for residue in range(m):
                    scores=self.proposals(plain,m,ks,residue,4)
                    assert float(scores.max()-scores[plain[residue]])<1e-8
                self.counts['independent_fourgram_coordinate_optima']+=1
            final.append((last,plain,key,cs,ks))
        ranked=[];seen=set()
        for row in sorted(final,key=lambda x:x[0],reverse=True):
            if tuple(row[1]) not in seen:ranked.append(row);seen.add(tuple(row[1]))
        for row,expected in zip(result['top'],ranked[:3]):
            score,plain,key,cs,ks=expected;recipe=row['recipe']
            assert to_indices(row['plaintext_runes'])==plain and abs(row['score']-score)<1e-9
            assert recipe=={'key_indices':key,'cipher_sign':cs,'feedback_sign':ks,'skip_positions':[],'skip_policy':'none'}
            queue=key[:];cipher_again=[]
            for i,p in enumerate(plain):cipher_again.append(cs*(p-ks*queue[i])%29);queue.append(p)
            assert cipher_again==cipher;self.counts['reencryptions']+=1
        assert len(result['top'])==len(ranked[:3])
        for name in ('coordinate','beam'):
            assert result['branch_best_before_refinement'][name]==max(r['score'] for r in pool if r['origin']==name)

    def source(self,index,source):
        chapter=('X','XI','XII')[index%3];start,n=((6800,300),(7300,300),(12750,200),(15000,729))[index//3]
        m=((13,23,31),(4,8,12),(13,23,31),(13,23,31))[index//3][index%3]
        raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
        plain=[];ranges=[];cursor=0
        for row in self.rows:
            if row['chapter']!=chapter:continue
            a,b=row['source_character_range'];words,_,_=tokenize(raw[a:b]);piece=[x for w in words for x in w]
            low=max(0,start-cursor);high=min(len(piece),start+n-cursor)
            if low<high:
                plain+=piece[low:high];ranges.append({'source_character_range':[a,b],'paragraph':row['paragraph'],'paragraph_rune_range':[low,high]})
            cursor+=len(piece)
            if cursor>=start+n:break
        rng=random.Random(3301062+index);key=[rng.randrange(29) for _ in range(m)]
        cs,ks=((1,-1),(1,1),(-1,-1),(-1,1))[index%4];queue=key[:];cipher=[]
        for i,p in enumerate(plain):cipher.append(cs*(p-ks*queue[i])%29);queue.append(p)
        assert len(plain)==n and to_indices(source['truth_runes'])==plain
        assert source['source_ranges']==ranges and source['chapter']==chapter and source['chapter_rune_range']==[start,start+n]
        assert source['injected_key']==key and source['cipher_sign']==cs and source['feedback_sign']==ks
        assert source['ciphertext_indices']==cipher


def main():
    tick=time.perf_counter();complete=load('checkpoints/phase22_controls_complete.json');v=Verifier();entries=[];controls=[]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    by_output={e['output']:e for e in events if e['status']=='completed'};null_score=None;original_null_score=None
    for path in complete['outputs']+load('checkpoints/phase22_endpoint_complete.json')['outputs']:
        assert time.perf_counter()-tick<900
        event=by_output[path];assert sha(path)==event['output_sha256']
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);assert row['training']==v.training
        if row['kind']=='control':v.source(row['index'],row['source'])
        else:
            original=load(next(p for p in complete['outputs'] if load(p)['kind']=='control' and load(p)['index']==2))['source']['ciphertext_indices']
            rng=random.Random(3302062);doublets=lambda a:sum(x==y for x,y in zip(a,a[1:]))
            for proposals in range(1,100001):
                if row['kind']=='null_endpoints':
                    middle=original[1:-1];rng.shuffle(middle);sample=original[:1]+middle+original[-1:]
                else:sample=original[:];rng.shuffle(sample)
                if doublets(sample)==doublets(original):break
            else:raise AssertionError('Rejection cap')
            assert sample==row['source']['ciphertext_indices'] and proposals==row['source']['proposals']
        v.result(row['source']['ciphertext_indices'],row['result'])
        if row['kind']=='control':
            exact=row['result']['top'][0]['plaintext_runes']==row['source']['truth_runes'];assert row['exact']==exact
            recipe=row['result']['top'][0]['recipe'];source=row['source']
            assert row['injected_recipe_exact']==(recipe['key_indices']==source['injected_key'] and recipe['cipher_sign']==source['cipher_sign'] and recipe['feedback_sign']==source['feedback_sign'])
            assert row['correct_runes']==sum(a==b for a,b in zip(to_indices(row['result']['top'][0]['plaintext_runes']),to_indices(source['truth_runes'])))
            controls.append({'index':row['index'],'runes':len(row['source']['ciphertext_indices']),'key_length':len(row['source']['injected_key']),
                'exact':exact,'injected_recipe_exact':row['injected_recipe_exact'],'correct_runes':row['correct_runes'],'output':path})
        elif row['kind']=='null_endpoints':null_score=row['result']['top'][0]['score']
        else:original_null_score=row['result']['top'][0]['score']
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        print({'verified':event['experiment'],**v.counts},flush=True)
    stage_a=all(r['exact'] for r in controls[:6]);assert complete['stage_A_passed']==stage_a
    assert len(controls)==(12 if stage_a else 6)
    gate=len(controls)==12 and all(r['exact'] for r in controls)
    assert complete['full_gate_passed']==gate and complete['null_score']==original_null_score and null_score is not None
    processes=load('results/phase22_controls_processes.json')+load('results/phase22_endpoint_processes.json')
    assert all(r['exit_code']==0 and r['reason'] is None and r['peak_sampled_bytes']<=768*1024**2 for r in processes)
    summary={'full_gate_passed':gate,'controls':controls,'null_score':null_score,'entries':entries,'validation':dict(v.counts),
        'original_noncompliant_null_score':original_null_score,'null_deviation':'Original E062-null-2 did not preserve endpoints. Preserved and separately verified; E062-null-endpoints supplies planned diagnostic with unchanged solver.',
        'seconds':sum(by_output[e['output']]['wall_seconds'] for e in entries),'peak_sampled_bytes':max(r['peak_sampled_bytes'] for r in processes),
        'validation_seconds':time.perf_counter()-tick,'new_decryptions':[]}
    (ROOT/'results/phase22_controls_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in summary.items() if k not in ('entries','controls')},flush=True)


if __name__=='__main__':main()
