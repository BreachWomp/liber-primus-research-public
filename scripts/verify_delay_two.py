"""Independent queue-vector exhaustive prefix verification; no production affine chain."""
from collections import Counter
import hashlib
import itertools
import json
import random
import time
import numpy as np
from verify_affine_feedback import AffineVerifier,ROOT,load,sha,to_indices
from verify_bilinear_feedback import BilinearVerifier
from verify_affine_feedback_unknown import CombinedVerifier
from verify_autokey_sections import SectionVerifier
from affine_feedback_factors import period_scores


class DelayTwoVerifier(AffineVerifier):
    source_anchors=CombinedVerifier.source_anchors
    spans=SectionVerifier.spans
    null=SectionVerifier.null

    def queue_scores(self,cipher,a,b,c):
        prefixes=np.array(list(itertools.product(range(29),repeat=2)),dtype=np.int16)
        total=np.zeros(len(prefixes));recent=[]
        for i,x in enumerate(cipher):
            p=prefixes[:,i] if i<2 else (a*x+b*recent[-2]+c)%29
            recent.append(p)
            if len(recent)>4:recent.pop(0)
            # Tables were independently checked entry-by-entry against scalar
            # probabilities in BilinearVerifier; reuse their exact rounding here.
            total+=self.lookup[len(recent)-1][tuple(recent)]
        self.counts['independent_full_prefix_scores']+=len(prefixes)
        return prefixes,total/len(cipher)

    def result(self,cipher,result):
        assert result['prefixes_per_retained_family']==841 and result['total_prefix_evaluations']==107648
        scores=period_scores(cipher,2,self.lookup[0],time.perf_counter()+30)
        assert hashlib.sha256(scores.astype('<f8').tobytes()).hexdigest()==result['screen_audit']['score_sha256']
        self.counts['replayed_family_scores']+=22736
        order=np.argsort(-np.round(scores.ravel(),9),kind='stable')
        audit=result['screen_audit'];assert audit['families']==22736 and audit['retained']==128
        if 'probe' in audit:
            a,b,c=audit['probe']['family'];flat=np.ravel_multi_index((a-1,b-1,c),scores.shape)
            assert audit['probe']['rank']==int(np.flatnonzero(order==flat)[0])+1
            assert abs(self.direct_score(cipher,2,a,b,c)-audit['probe']['score'])<1e-7
        finals=[]
        assert len(result['families'])==128
        for rank,(flat,row) in enumerate(zip(order[:128],result['families']),1):
            ai,bi,ci=np.unravel_index(flat,scores.shape);a,b,c=int(ai)+1,int(bi)+1,int(ci)
            assert (row['a'],row['b'],row['c'],row['rank'])==(a,b,c,rank)
            assert abs(self.direct_score(cipher,2,a,b,c)-row['unigram_max_total'])<1e-7
            self.counts['independent_retained_family_scores']+=1
            prefixes,exact=self.queue_scores(cipher,a,b,c)
            assert hashlib.sha256(exact.astype('<f8').tobytes()).hexdigest()==row['prefix_scores_sha256']
            take=np.argsort(-exact,kind='stable')[:3]
            assert len(row['top_prefixes'])==3
            for k,top in zip(take,row['top_prefixes']):
                assert prefixes[k].tolist()==top['prefix'] and abs(float(exact[k])-top['score'])<1e-9
                plain,key=self.decode(cipher,top['prefix'],a,b,c)
                assert abs(self.score(plain)-top['score'])<1e-9
                finals.append((top['score'],plain,key,a,b,c))
            self.counts['independent_family_optima']+=1
        ranked=[];seen=set()
        for r in sorted(finals,key=lambda r:r[0],reverse=True):
            if tuple(r[1]) not in seen:ranked.append(r);seen.add(tuple(r[1]))
        assert len(result['top'])==len(ranked[:3])
        for top,(score,plain,key,a,b,c) in zip(result['top'],ranked[:3]):
            assert top['score']==score and to_indices(top['plaintext_runes'])==plain
            assert top['recipe']=={'key_indices':key,'cipher_sign':a,'feedback_sign':b,'constant':c,'skip_positions':[],'skip_policy':'none'}
            inv=next(k for k in range(1,29) if a*k%29==1);queue=key[:];again=[]
            for i,p in enumerate(plain):again.append(inv*(p-b*queue[i]-c)%29);queue.append(p)
            assert again==cipher;self.counts['reencryptions']+=1

    def source_two(self,index,source):
        base_index=(index%3 if index<9 else 3+index%3) if index<12 else (0,3,6,11)[index-12]
        original=load(next(r['output'] for r in load('results/phase25_controls_validation.json')['controls'] if r['index']==base_index))['source']
        BilinearVerifier.source_general(self,base_index,original)
        n=(66,95,200,300)[index//3] if index<12 else len(original['ciphertext_indices'])
        a,b=((2,7,14,27)[index%4],(1,3,15,28)[index%4]) if index<12 else ((1,1),(1,28),(28,1),(28,28))[index-12]
        c=(5*index+1)%28+1 if index<12 else 0
        rng=random.Random(3301078+index);key=[rng.randrange(29) for _ in range(2)]
        assert source['base_source']==original and source['base_control_index']==base_index and source['take_runes']==n
        plain=to_indices(original['truth_runes'])[:n]
        assert to_indices(source['truth_runes'])==plain and source['injected_key']==key
        assert (source['cipher_sign'],source['feedback_sign'],source['constant'])==(a,b,c)
        queue=key[:];cipher=[];inv=next(k for k in range(1,29) if a*k%29==1)
        for i,p in enumerate(plain):cipher.append(inv*(p-b*queue[i]-c)%29);queue.append(p)
        assert source['ciphertext_indices']==cipher


def main():
    tick=time.perf_counter();v=DelayTwoVerifier();complete=load('checkpoints/phase28_controls_complete.json')
    benchmark=load('checkpoints/phase28_benchmark_complete.json')['output']
    paths=[benchmark]+complete['outputs'];events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    by_output={e['output']:e for e in events if e['status']=='completed'};entries=[];controls=[]
    for path in paths:
        assert time.perf_counter()-tick<900
        event=by_output[path];assert sha(path)==event['output_sha256']
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);assert row['parameters']==load('experiments/delay_two_plan.json') and row['training']==v.training
        if path==benchmark:
            rng=random.Random(3302077);cipher=[rng.randrange(29) for _ in range(3316)]
            assert row['ciphertext_indices']==cipher and row['gate_passed'] and row['literal_prefix_comparisons']==2523
        else:
            source=row['source'];cipher=source['ciphertext_indices']
            if row['kind']=='control':v.source_two(row['index'],source)
            else:
                original=load(next(p for p in complete['outputs'] if load(p)['kind']=='control' and load(p)['index']==5))['source']['ciphertext_indices']
                rng=random.Random(3302078);eq=lambda x:sum(a==b for a,b in zip(x,x[1:]))
                for proposals in range(1,100001):
                    mid=original[1:-1];rng.shuffle(mid);sample=original[:1]+mid+original[-1:]
                    if eq(sample)==eq(original):break
                assert source['proposals']==proposals and cipher==sample and Counter(cipher)==Counter(original)
        v.result(cipher,row['result'])
        if path!=benchmark and row['kind']=='control':
            top=row['result']['top'][0];s=row['source'];r=top['recipe']
            exact=top['plaintext_runes']==s['truth_runes'];recipe=all(r[k]==s[j] for k,j in [('key_indices','injected_key'),('cipher_sign','cipher_sign'),('feedback_sign','feedback_sign'),('constant','constant')])
            assert row['exact']==exact and row['injected_recipe_exact']==recipe
            rank=row['result']['screen_audit']['probe']['rank'];assert rank==row['injected_family_rank']
            assert row['injected_family_retained']==(rank<=128)
            controls.append({'index':row['index'],'runes':len(cipher),'exact':exact,'recipe_exact':recipe,'family_rank':rank,
                'a':s['cipher_sign'],'b':s['feedback_sign'],'c':s['constant'],'output':path})
        elif path!=benchmark:null_score=row['result']['top'][0]['score']
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        print({'verified':event['experiment'],'seconds':time.perf_counter()-tick},flush=True)
    gate=all(r['exact'] and r['recipe_exact'] and r['family_rank']<=128 for r in controls)
    assert len(controls)==16 and gate==complete['full_gate_passed'] and null_score==complete['null_score']
    result={'full_gate_passed':gate,'controls':controls,'null_score':null_score,'entries':entries,'validation':dict(v.counts),
        'validation_seconds':time.perf_counter()-tick,'verifier_sha256':sha('scripts/verify_delay_two.py'),
        'seconds':sum(by_output[p]['wall_seconds'] for p in paths),'new_decryptions':[]}
    (ROOT/'results/phase28_controls_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in result.items() if k not in ('controls','entries')})


if __name__=='__main__':main()
