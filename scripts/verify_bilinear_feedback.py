"""Independent literal family scoring and scalar queue audit for E068."""
from collections import Counter
import json
import random
import time
import numpy as np
from verify_general_feedback import GeneralVerifier,ROOT,load,sha,tokenize,to_indices


class BilinearVerifier(GeneralVerifier):
    def __init__(self):
        super().__init__()
        # Build every probability through scalar model evaluation, independently
        # of the research runner's count-array construction.
        self.reference=[]
        for order in range(1,5):
            shape=(29,)*order
            table=np.fromiter((self.model._logp(t[:-1],t[-1]) for t in np.ndindex(shape)),dtype=float,count=29**order).reshape(shape)
            assert np.allclose(table,self.lookup[order-1],rtol=0,atol=1e-12)
            self.reference.append(table)
            self.counts['scalar_model_table_entries']+=table.size
        rng=random.Random(3309068)
        for n in (1,2,3,4,200,3316):
            values=[rng.randrange(29) for _ in range(n)]
            for order in (3,4):
                assert abs(self.score(values,order)-GeneralVerifier.score(self,values,order))<1e-10
                self.counts['reference_sequence_crosschecks']+=1

    def score(self,plain,order=4):
        values=np.array(plain);n=len(values);total=0.0
        for end in range(min(order-1,n)):
            total+=self.reference[end][tuple(values[:end+1])]
        if n>=order:
            total+=self.reference[order-1][tuple(values[j:n-order+j+1] for j in range(order))].sum()
        return float(total/n)

    def screen(self,cipher,records):
        assert len(records)==22736
        by_key={(r['period'],r['cipher_sign'],r['feedback_sign']):r for r in records}
        assert len(by_key)==22736
        expected=[]
        for m in range(4,33):
            scores=np.zeros((28,28))
            for b in range(1,29):
                base,_=self.decode(cipher,[0]*m,1,b)
                one,_=self.decode(cipher,[1]*m,1,b)
                coeff=(np.array(one,dtype=np.int16)-np.array(base,dtype=np.int16))%29
                self.coefficients[len(cipher),m,b]=coeff
                # Direct symbol enumeration, no histograms or prefix rescaling.
                symbols=(np.arange(1,29,dtype=np.int16)[:,None,None]*np.array(base,dtype=np.int16)[None,None,:]+np.arange(29,dtype=np.int16)[None,:,None]*coeff[None,None,:])%29
                for r in range(m):
                    scores[:,b-1]+=self.lookup[0][symbols[:,:,r::m]].sum(axis=2).max(axis=1)
            rows=[]
            for a in range(1,29):
                for b in range(1,29):
                    row=by_key[m,a,b]
                    assert abs(row['unigram_max_total']-scores[a-1,b-1])<1e-7
                    assert row['selection_score']==round(row['unigram_max_total'],9)
                    rows.append(row)
            # Ranking uses prescribed rounded stored scores after independent
            # numerical verification; avoid treating sum-order rounding as a cipher difference.
            ranked=sorted(rows,key=lambda r:r['selection_score'],reverse=True)
            assert [r['rank'] for r in ranked]==list(range(1,785))
            expected+=ranked
        assert records==expected
        self.counts['independent_family_screen_scores']+=len(records)

    def source_general(self,index,source):
        if index>=12:
            old_index=(2,5,8,11)[index-12]
            entry=next(r for r in load('results/phase24_controls_validation.json')['controls'] if r['index']==old_index)
            original=load(entry['output'])['source']
            assert source==original|{'cipher_sign':original['cipher_sign']%29,'reused_input_control':f'E066-control-{old_index}'}
            GeneralVerifier.source_general(self,old_index,original)
            return
        chapter=('X','XI','XII')[index%3]
        start,n=((12750,200),(6800,300),(15000,729),(1000,3316))[index//3]
        m=32 if index==11 else (13,23,31)[index%3];cs=(2,7,14,27)[index%4];ks=(3,8,15,26)[(index//3+index)%4]
        raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
        plain=[];ranges=[];cursor=0
        for row in self.rows:
            if row['chapter']!=chapter:continue
            a,b=row['source_character_range'];words,_,_=tokenize(raw[a:b]);piece=[x for w in words for x in w]
            lo=max(0,start-cursor);hi=min(len(piece),start+n-cursor)
            if lo<hi:
                plain+=piece[lo:hi];ranges.append({'source_character_range':[a,b],'paragraph':row['paragraph'],'paragraph_rune_range':[lo,hi]})
            cursor+=len(piece)
            if cursor>=start+n:break
        rng=random.Random(3301068+index);key=[rng.randrange(29) for _ in range(m)]
        queue=key[:];cipher=[]
        for i,p in enumerate(plain):cipher.append(next(x for x in range(1,29) if cs*x%29==1)*(p-ks*queue[i])%29);queue.append(p)
        assert len(plain)==n and to_indices(source['truth_runes'])==plain
        assert source['source_ranges']==ranges and source['chapter']==chapter and source['chapter_rune_range']==[start,start+n]
        assert source['injected_key']==key and source['cipher_sign']==cs and source['feedback_sign']==ks
        assert source['ciphertext_indices']==cipher

    def result(self,cipher,result):
        n=len(cipher);self.screen(cipher,result['screening'])
        expected=[(f['period'],f['cipher_sign'],f['feedback_sign']) for f in result['screening'] if f['rank']<=8]
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
            for i,p in enumerate(plain):cipher_again.append(next(x for x in range(1,29) if cs*x%29==1)*(p-ks*queue[i])%29);queue.append(p)
            assert cipher_again==cipher;self.counts['reencryptions']+=1
        assert len(result['top'])==len(ranked[:3])
        for name in ('coordinate','beam'):
            assert result['branch_best_before_refinement'][name]==max(r['score'] for r in pool if r['origin']==name)


def main():
    tick=time.perf_counter();complete=load('checkpoints/phase25_controls_complete.json');v=BilinearVerifier();entries=[];controls=[]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    by_output={e['output']:e for e in events if e['status']=='completed'}
    for path in complete['outputs']:
        assert time.perf_counter()-tick<1800
        event=by_output[path];assert sha(path)==event['output_sha256']
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);assert row['training']==v.training and row['parameters']==load('experiments/bilinear_feedback_plan.json')
        if row['kind']=='control':v.source_general(row['index'],row['source'])
        else:
            original=load(next(p for p in complete['outputs'] if load(p)['kind']=='control' and load(p)['index']==5))['source']['ciphertext_indices']
            rng=random.Random(3302068);equal=lambda x:sum(a==b for a,b in zip(x,x[1:]))
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
            recipe=all(r[k]==source[s] for k,s in [('key_indices','injected_key'),('cipher_sign','cipher_sign'),('feedback_sign','feedback_sign')])
            assert row['injected_recipe_exact']==recipe
            injected=next(f for f in row['result']['screening'] if (f['period'],f['cipher_sign'],f['feedback_sign'])==(len(source['injected_key']),source['cipher_sign'],source['feedback_sign']))
            assert row['injected_family_rank']==injected['rank'] and row['injected_family_retained']==(injected['rank']<=8)
            assert row['correct_runes']==sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
            controls.append({'index':row['index'],'runes':len(source['ciphertext_indices']),'key_length':len(source['injected_key']),
                'cipher_sign':source['cipher_sign'],'feedback_sign':source['feedback_sign'],'family_rank':injected['rank'],
                'family_retained':row['injected_family_retained'],'exact':exact,'injected_recipe_exact':recipe,'correct_runes':row['correct_runes'],'output':path})
        else:null_score=row['result']['top'][0]['score']
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        print({'verified':event['experiment'],'seconds':time.perf_counter()-tick},flush=True)
    assert len(controls)==16 and len(entries)==17
    gate=all(r['exact'] and r['injected_recipe_exact'] and r['family_retained'] for r in controls)
    assert complete['full_gate_passed']==gate and complete['null_score']==null_score
    processes=load('results/phase25_controls_processes.json')
    assert all(r['exit_code']==0 and r['reason'] is None and r['peak_sampled_bytes']<=768*1024**2 for r in processes)
    summary={'full_gate_passed':gate,'controls':controls,'null_score':null_score,'entries':entries,'validation':dict(v.counts),
        'seconds':sum(by_output[e['output']]['wall_seconds'] for e in entries),'peak_sampled_bytes':max(r['peak_sampled_bytes'] for r in processes),
        'validation_seconds':time.perf_counter()-tick,'verifier_sha256':sha('scripts/verify_bilinear_feedback.py'),'new_decryptions':[]}
    (ROOT/'results/phase25_controls_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in summary.items() if k not in ('entries','controls')},flush=True)


if __name__=='__main__':main()
