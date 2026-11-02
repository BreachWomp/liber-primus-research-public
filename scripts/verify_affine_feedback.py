"""Independent constant-aware scalar queue and candidate audit; reused E068 score verifier."""
from collections import Counter
import json
import random
import time
import numpy as np
from verify_bilinear_feedback import BilinearVerifier,ROOT,load,sha,tokenize,to_indices
from phase26_provenance import verify_dependency
from affine_feedback_factors import screen as production_screen


class AffineVerifier(BilinearVerifier):
    def decode(self,cipher,prefix,cs,ks,c=0):
        inverse=next(x for x in range(1,29) if ks*x%29==1)
        key=[(p-cs*x-c)*inverse%29 for p,x in zip(prefix,cipher)]
        queue=key[:];plain=[]
        for i,x in enumerate(cipher):
            p=(cs*x+ks*queue[i]+c)%29;plain.append(p);queue.append(p)
        self.counts['scalar_decodings']+=1
        return plain,key

    def direct_score(self,cipher,m,a,b,c):
        zero,_=self.decode(cipher,[0]*m,a,b,c)
        one,_=self.decode(cipher,[1]*m,a,b,c)
        power=(np.array(one)-np.array(zero))%29
        self.coefficients[len(cipher),m,b]=power
        symbols=(np.array(zero)[None,:]+np.arange(29)[:,None]*power)%29
        return float(sum(self.reference[0][symbols[:,r::m]].sum(axis=1).max() for r in range(m)))

    def screen(self,cipher,result):
        probes=[r['probe']['family'] for r in result['screen_audit'] if 'probe' in r]
        assert len(probes)<=1
        # Replay is explicitly NOT an independent implementation of all659344 scores.
        rows,audit=production_screen(cipher,self.lookup[0],time.perf_counter()+120,probes[0] if probes else None)
        assert rows==result['screening'] and audit==result['screen_audit']
        self.counts['replayed_full_screen_scores']+=29*22736
        for r in rows:
            direct=self.direct_score(cipher,r['period'],r['cipher_sign'],r['feedback_sign'],r['constant'])
            assert abs(direct-r['unigram_max_total'])<1e-7
            self.counts['independent_retained_family_scores']+=1
        for r in audit:
            if 'probe' in r:
                m,a,b,c=r['probe']['family']
                assert abs(self.direct_score(cipher,m,a,b,c)-r['probe']['score'])<1e-7
                self.counts['independent_injected_family_scores']+=1

    def seed_check(self,cipher,f):
        m,a,b,c=f['period'],f['cipher_sign'],f['feedback_sign'],f['constant']
        zero,_=self.decode(cipher,[0]*m,a,b,c)
        one,_=self.decode(cipher,[1]*m,a,b,c)
        power=(np.array(one)-np.array(zero))%29
        symbols=(np.array(zero)[None,:]+np.arange(29)[:,None]*power)%29
        unary=np.array([self.lookup[0][symbols[:,r::m]].sum(axis=1) for r in range(m)])
        ranks=np.argsort(-unary,axis=1,kind='stable')
        rng=random.Random(3303072+22736*m+812*(a-1)+29*(b-1)+c)
        for i,start in enumerate(f['starts']):
            prefix=[int(ranks[r,i if i<3 else rng.randrange(5)]) for r in range(m)]
            assert prefix==start['initial']
            self.counts['seeded_initializers_checked']+=1

    def source_affine(self,index,source):
        old_index=index if index<12 else (0,3,6,11)[index-12]
        entry=next(r for r in load('results/phase25_controls_validation.json')['controls'] if r['index']==old_index)
        original=load(entry['output'])['source']
        # This performs raw-source tokenization and independently checks old provenance.
        BilinearVerifier.source_general(self,old_index,original)
        if index>=12:
            assert source==original|{'constant':0,'reused_input_control':f'E068-control-{old_index}'}
            return
        a=(2,7,14,27)[index%4];b=(1,3,15)[index%3];c=(5*index+1)%28+1
        rng=random.Random(3301072+index);key=[rng.randrange(29) for _ in original['injected_key']]
        plain=to_indices(original['truth_runes']);queue=key[:];cipher=[]
        inv=next(x for x in range(1,29) if a*x%29==1)
        for i,p in enumerate(plain):
            cipher.append(inv*(p-b*queue[i]-c)%29);queue.append(p)
        assert source==original|{'injected_key':key,'cipher_sign':a,'feedback_sign':b,'constant':c,'ciphertext_indices':cipher}

    def result(self,cipher,result):
        n=len(cipher);self.screen(cipher,result)
        expected=[(f['period'],f['cipher_sign'],f['feedback_sign'],f['constant']) for f in result['screening'] if f['rank']<=8]
        assert [(f['period'],f['cipher_sign'],f['feedback_sign'],f['constant']) for f in result['families']]==expected
        pool=[]
        for f in result['families']:
            m,cs,ks,c=f['period'],f['cipher_sign'],f['feedback_sign'],f['constant'];assert len(f['starts'])==8
            self.seed_check(cipher,f)
            for start in f['starts']:
                initial,_=self.decode(cipher,start['initial'],cs,ks,c);plain,_=self.decode(cipher,start['prefix'],cs,ks,c)
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
                assert (row['period'],row['cipher_sign'],row['feedback_sign'],row['constant'])==(m,cs,ks,c)
                plain,key=self.decode(cipher,row['prefix'],cs,ks,c)
                assert abs(self.score(plain)-row['score'])<1e-9
                assert abs(self.score(plain,3)-row['trigram_score'])<1e-9
                self.counts['candidate_score_pairs']+=1;pool.append(row)
        selected=[];seen=set()
        for row in sorted(pool,key=lambda x:x['score'],reverse=True):
            ident=(row['period'],row['cipher_sign'],row['feedback_sign'],row['constant'],tuple(row['prefix']))
            if ident not in seen:seen.add(ident);selected.append(row)
            if len(selected)==12:break
        assert [r['initial'] for r in result['refinements']]==selected
        final=[]
        for refinement in result['refinements']:
            r=refinement['initial'];m,cs,ks,c=r['period'],r['cipher_sign'],r['feedback_sign'],r['constant'];last=r['score']
            assert 1<=len(refinement['trace'])<=6
            for row in refinement['trace']:
                plain,key=self.decode(cipher,row['prefix'],cs,ks,c);score=self.score(plain)
                assert abs(score-row['score'])<1e-9 and score>=last-1e-9;last=score
                self.counts['fourgram_trace_scores']+=1
            if refinement['converged']:
                for residue in range(m):
                    scores=self.proposals(plain,m,ks,residue,4)
                    assert float(scores.max()-scores[plain[residue]])<1e-8
                self.counts['independent_fourgram_coordinate_optima']+=1
            final.append((last,plain,key,cs,ks,c))
        ranked=[];seen=set()
        for row in sorted(final,key=lambda x:x[0],reverse=True):
            if tuple(row[1]) not in seen:ranked.append(row);seen.add(tuple(row[1]))
        for row,expected in zip(result['top'],ranked[:3]):
            score,plain,key,cs,ks,c=expected;recipe=row['recipe']
            assert to_indices(row['plaintext_runes'])==plain and abs(row['score']-score)<1e-9
            assert recipe=={'key_indices':key,'cipher_sign':cs,'feedback_sign':ks,'constant':c,'skip_positions':[],'skip_policy':'none'}
            queue=key[:];cipher_again=[]
            for i,p in enumerate(plain):cipher_again.append(next(x for x in range(1,29) if cs*x%29==1)*(p-ks*queue[i]-c)%29);queue.append(p)
            assert cipher_again==cipher;self.counts['reencryptions']+=1
        assert len(result['top'])==len(ranked[:3])
        for name in ('coordinate','beam'):
            assert result['branch_best_before_refinement'][name]==max(r['score'] for r in pool if r['origin']==name)


def main():
    tick=time.perf_counter();complete=load('checkpoints/phase26_controls_complete.json');v=AffineVerifier();entries=[];controls=[]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    by_output={e['output']:e for e in events if e['status']=='completed'}
    for path in complete['outputs']:
        assert time.perf_counter()-tick<1800
        event=by_output[path];assert sha(path)==event['output_sha256']
        for dep,digest in event['input_dependencies'].items():verify_dependency(dep,digest)
        row=load(path);assert row['training']==v.training and row['parameters']==load('experiments/delayed_affine_feedback_plan.json')
        if row['kind']=='control':v.source_affine(row['index'],row['source'])
        else:
            original=load(next(p for p in complete['outputs'] if load(p)['kind']=='control' and load(p)['index']==5))['source']['ciphertext_indices']
            rng=random.Random(3302072);equal=lambda x:sum(a==b for a,b in zip(x,x[1:]))
            for proposals in range(1,100001):
                middle=original[1:-1];rng.shuffle(middle);sample=original[:1]+middle+original[-1:]
                if equal(sample)==equal(original):break
            else:raise AssertionError('Null rejection cap')
            assert sample==row['source']['ciphertext_indices'] and proposals==row['source']['proposals']
            assert Counter(sample)==Counter(original)
        v.result(row['source']['ciphertext_indices'],row['result'])
        if row['kind']=='control':
            source=row['source'];top=row['result']['top'][0];r=top['recipe']
            exact=top['plaintext_runes']==source['truth_runes'];assert row['exact']==exact
            recipe=all(r[k]==source[s] for k,s in [('key_indices','injected_key'),('cipher_sign','cipher_sign'),('feedback_sign','feedback_sign'),('constant','constant')])
            assert row['injected_recipe_exact']==recipe
            injected=next(r['probe'] for r in row['result']['screen_audit'] if 'probe' in r)
            assert row['injected_family_rank']==injected['rank'] and row['injected_family_retained']==(injected['rank']<=8)
            assert row['correct_runes']==sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
            controls.append({'index':row['index'],'runes':len(source['ciphertext_indices']),'key_length':len(source['injected_key']),
                'cipher_sign':source['cipher_sign'],'feedback_sign':source['feedback_sign'],'constant':source['constant'],'family_rank':injected['rank'],
                'family_retained':row['injected_family_retained'],'exact':exact,'injected_recipe_exact':recipe,'correct_runes':row['correct_runes'],'output':path})
        else:null_score=row['result']['top'][0]['score']
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        print({'verified':event['experiment'],'seconds':time.perf_counter()-tick},flush=True)
    assert len(controls)==16 and len(entries)==17
    gate=all(r['exact'] and r['injected_recipe_exact'] and r['family_retained'] for r in controls)
    assert complete['full_gate_passed']==gate and complete['null_score']==null_score
    processes=load('results/phase26_controls_processes.json')
    assert all(r['exit_code']==0 and r['reason'] is None and r['peak_sampled_bytes']<=768*1024**2 for r in processes)
    summary={'full_gate_passed':gate,'controls':controls,'null_score':null_score,'entries':entries,'validation':dict(v.counts),
        'seconds':sum(by_output[e['output']]['wall_seconds'] for e in entries),'peak_sampled_bytes':max(r['peak_sampled_bytes'] for r in processes),
        'validation_seconds':time.perf_counter()-tick,'verifier_sha256':sha('scripts/verify_affine_feedback.py'),'verification_limits':'All full screens replayed. Independent direct queues validate every retained family and injected family; E071 independently enumerates27608 families. This is not a separate full-grid implementation for every input.', 'new_decryptions':[]}
    (ROOT/'results/phase26_controls_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in summary.items() if k not in ('entries','controls')},flush=True)


if __name__=='__main__':main()
