"""Independent scalar replay of E052, including source ranges and selection."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'experiments'))
from attack_support import to_indices,to_runes
from heldout_language import corpus,tokenize
from liberprimus.decoding import BackoffModel
from finalize_phase17 import scalar_replay,schedule_optimum,canonical


def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


class Verifier:
    def __init__(self):
        self.rows=corpus();self.raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
        selected=[r for r in self.rows if r['chapter'] in ('I','III','IV','V','VI','VII','VIII','IX')]
        self.ranges=[r['source_character_range'] for r in selected]
        sequences=[[x for w in tokenize(self.raw[a:b])[0] for x in w] for a,b in self.ranges]
        self.model=BackoffModel(sequences,order=4,alpha=.5,strength=5)
        self.counts=Counter()

    def language(self,plain,order):
        return sum(self.model.logp(tuple(plain[max(0,i-order+1):i]),symbol) for i,symbol in enumerate(plain))

    def pool_row(self,pool,spans,row,optimum=False):
        key=row['key'];m=len(key);sign=row['sign'];phases=row['page_phases'];order=row['order']
        assert m==len(canonical(key)) and 1<=m<=32 and order in (1,2,4)
        assert len(phases)==len(spans) and phases[0]==0 and all(0<=p<m for p in phases)
        total=0.
        for s,p in zip(spans,phases):
            part=pool[s['start']:s['end']]
            plain=scalar_replay(part,key[p:]+key[:p],sign,[])
            value=self.language(plain,order);total+=value
            if optimum:
                best=max(self.language([(sign*c+key[(i+phase)%m])%29 for i,c in enumerate(part)],order) for phase in range(m))
                assert abs(best-value)<1e-7
        assert abs(total/len(pool)-row['language_score'])<1e-9
        assert abs((total-m*math.log(29)-(len(spans)-1)*math.log(m))/len(pool)-row['score'])<1e-9
        self.counts['pool_records_recomputed']+=1
        if optimum:self.counts['independent_pool_phase_optima']+=1

    def stream_row(self,cipher,row):
        key=row['key'];assert 1<=len(key)<=32 and len(canonical(key))==len(key)
        plain=scalar_replay(cipher,key,row['sign'],row['skip_positions'])
        language=self.language(plain,4)/len(cipher)
        assert abs(language-row['language_score'])<1e-9
        assert abs(language-(len(key)*math.log(29)+cipher.count(0)*math.log(2))/len(cipher)-row['score'])<1e-9
        assert row['dp_max_states']<=8*row['input_period'] and row['input_period']<=32
        assert 0<=row['selected_phase']<row['input_period']
        if 'plaintext_runes' in row:assert to_runes(plain)==row['plaintext_runes']
        self.counts['stream_records_recomputed']+=1

    def result(self,cipher,result):
        intervals=[];begin=0
        for i,c in enumerate(cipher+[0]):
            if c==0:
                if i-begin>=16:intervals.append((begin,i))
                begin=i+1
        ranges=[[a,min(b,a+256)] for a,b in sorted(intervals,key=lambda ab:(-(ab[1]-ab[0]),ab[0]))[:12]]
        pool=[];spans=[]
        for j,(a,b) in enumerate(ranges):
            start=len(pool);pool+=cipher[a:b]
            spans.append({'page_id':f'fragment-{j:02}','start':start,'end':len(pool),'runes':b-a,'zero_rune_page':False})
        assert pool==result['pool_ciphertext'] and spans==result['pool_spans'] and ranges==result['pool_source_ranges']
        assert 0 not in pool and len(result['unigram_starts'])==512 and len(result['families'])==32
        for row in result['unigram_starts']:
            assert 1<=row['unigram_steps']<=20
            self.pool_row(pool,spans,row)
        winners=[]
        for family in result['families']:
            m,sign=family['nominal_period'],family['sign'];assert 17<=m<=32 and sign in (1,-1)
            starts=[r for r in result['unigram_starts'] if r['nominal_period']==m and r['sign']==sign]
            assert [r['start'] for r in starts]==list(range(16))
            unique={}
            for row in starts:
                ident=tuple(canonical(row['key']))
                if ident not in unique or row['score']>unique[ident]['score']:unique[ident]=row
            retained=sorted(unique.values(),key=lambda r:r['score'],reverse=True)[:2]
            assert [c['initial'] for c in family['candidates']]==retained
            for candidate in family['candidates']:
                trace=candidate['pool_trace'];assert len(trace)==8
                assert [r['order'] for r in trace]==[2]*4+[4]*4
                for row in trace:self.pool_row(pool,spans,row)
                for a,b in zip(trace,trace[1:]):
                    if a['order']==b['order']:assert b['score']>=a['score']-1e-9
                assert candidate['state']==trace[-1] and candidate['nominal_period']==m
            winner=max(range(len(retained)),key=lambda i:family['candidates'][i]['state']['score'])
            assert winner==family['winner'];chosen=family['candidates'][winner];winners.append(chosen)
            self.pool_row(pool,spans,chosen['state'],optimum=True)
        selected=[max((r for r in winners if r['nominal_period']==m),key=lambda r:r['state']['score']) for m in range(17,33)]
        remaining=[r for r in winners if all(r is not s for s in selected)]
        selected+=sorted(remaining,key=lambda r:r['state']['score'],reverse=True)[:4]
        assert len(result['restarts'])==20;finals=[]
        for i,(restart,choice) in enumerate(zip(result['restarts'],selected)):
            assert restart['pool_state']==choice['state'] and restart['pool_start']==choice['initial']['start']
            assert restart['nominal_period']==choice['nominal_period']
            trace=restart['trace'];assert 2<=len(trace)<=4
            for row in trace:self.stream_row(cipher,row)
            assert all(b['score']>=a['score']-1e-9 for a,b in zip(trace,trace[1:]))
            final=restart['final'];assert all(final[k]==v for k,v in trace[-1].items()) and final['seed_index']==i
            self.stream_row(cipher,final);finals.append(final)
        ranked=[];seen=set()
        for row in sorted(finals,key=lambda r:r['score'],reverse=True):
            if row['plaintext_runes'] not in seen:ranked.append(row);seen.add(row['plaintext_runes'])
        assert result['top']==ranked[:3]
        best=ranked[0]
        assert abs(schedule_optimum(cipher,best['key'],best['sign'],self.model)-best['language_score'])<1e-9
        self.counts['independent_stream_optima']+=1

    def source(self,data):
        assert data['training']['training_source_ranges']==self.ranges
        assert data['training']['source_sha256']==sha('data/raw/gutenberg/pg2944.txt')
        source=data['source'];kind=data['kind'];index=data['index']
        if kind=='regression':
            old=load('results/E049-long-key-controls-74c0828cc750.json')['controls'][index]
            assert source=={k:v for k,v in old.items() if k not in ('result','checks','exact')}
        chapter=('X','XI','XII')[index]
        if kind=='fresh':
            full=[];expected=[]
            for r in self.rows:
                if r['chapter']!=chapter:continue
                a,b=r['source_character_range'];piece=[x for w in tokenize(self.raw[a:b])[0] for x in w]
                start=max(0,4000-len(full));end=min(len(piece),5200-len(full))
                if start<end:expected.append({'source_character_range':[a,b],'paragraph':r['paragraph'],'paragraph_rune_range':[start,end]})
                full+=piece
                if len(full)>=5200:break
            plain=full[4000:5200]
            assert expected==source['source_ranges'] and source['chapter_rune_range']==[4000,5200]
            assert to_runes(plain)==source['truth_runes']
            rng=random.Random(3301052)
        else:
            plain=[]
            for r in source['source_ranges']:
                a,b=r['source_character_range'];plain += [x for w in tokenize(self.raw[a:b])[0] for x in w][:r['runes_consumed']]
            assert to_runes(plain)==source['truth_runes']
            rng=random.Random(3301049)
        for j in range(index+1):key=[rng.randrange(1,29) for _ in range((17,23,31)[j])]
        skips=[i for i,c in enumerate(plain) if c==0][::2];sign=(1,-1,1)[index]
        assert source['injected_key']==key and source['injected_skips']==skips and source['injected_sign']==sign
        assert scalar_replay(source['ciphertext_indices'],key,sign,skips)==plain
        for r in source['source_ranges']:
            a,b=r['source_character_range'];assert all(b<=x or a>=y for x,y in self.ranges)
        top=data['result']['top'][0]
        expected={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
                  'key_exact':top['key']==key and top['sign']==sign,'mask_exact':top['skip_positions']==skips}
        assert data['checks']==expected and data['exact']==all(expected.values())
        assert data['correct_runes']==sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),plain))

    def null(self,source,record):
        assert source['page_spans']==record['page_spans'];out=[];records=[]
        equal=lambda v:sum(a==b for a,b in zip(v,v[1:]))
        for i,span in enumerate(source['page_spans']):
            part=source['ciphertext_indices'][span['start']:span['end']];rng=random.Random(3302052+i)
            for proposals in range(1,100001):
                middle=part[1:-1];rng.shuffle(middle);sample=part[:1]+middle+part[-1:]
                if equal(sample)==equal(part):break
            else:raise AssertionError('Null rejection cap')
            assert Counter(sample)==Counter(part);out+=sample
            records.append({'page_id':span['page_id'],'seed':3302052+i,'proposals':proposals})
        assert out==record['ciphertext_indices'] and records==record['page_proposals']
        assert Counter(out)==Counter(source['ciphertext_indices']) and equal(out)==equal(source['ciphertext_indices'])


def verify():
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    latest={e['experiment']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E052-')}
    assert len(latest)==7
    verify=Verifier();data={};entries=[]
    for ident,event in latest.items():
        assert sha(event['output'])==event['output_sha256'] and event['wall_seconds']<180
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
        row=load(event['output']);data[ident]=row
        assert row['unknown_sections_searched']==0 and row['new_decryptions']==[]
        verify.result(row['source']['ciphertext_indices'],row['result'])
        if row['kind']!='null':verify.source(row)
        entries.append({'id':ident,'fingerprint':event['fingerprint'],'output':event['output'],'sha256':event['output_sha256']})
        print({'verified':ident,**verify.counts},flush=True)
    verify.null(data['E052-fresh-2']['source'],data['E052-null-2']['source'])
    controls=[]
    for row in data.values():
        if row['kind']=='null':continue
        s=row['source'];top=row['result']['top'][0];truth=to_indices(s['truth_runes'])
        truth_score=verify.model.score(truth)-(len(s['injected_key'])*math.log(29)+s['ciphertext_indices'].count(0)*math.log(2))/len(truth)
        controls.append({'kind':row['kind'],'chapter':s['chapter'],'key_length':len(s['injected_key']),
                         'runes':len(truth),'exact':row['exact'],'correct_runes':row['correct_runes'],
                         'found_score':top['score'],'truth_score':truth_score})
    processes=load('results/phase18_processes.json')
    assert len(processes)==7 and all(p['exit_code']==0 and p['reason'] is None and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    summary={'experiment':'E052','gate_passed':all(r['exact'] for r in controls),'controls':controls,
             'null_score':data['E052-null-2']['result']['top'][0]['score'],
             'seconds':sum(e['wall_seconds'] for e in latest.values()),'successful_tasks':len(latest),
             'peak_sampled_bytes':max(p['peak_sampled_bytes'] for p in processes),
             'validation':dict(verify.counts),'entries':entries,'new_decryptions':[]}
    assert summary['seconds']<1260
    (ROOT/'results/phase18_control_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary),flush=True)
    return summary


if __name__=='__main__':verify()
