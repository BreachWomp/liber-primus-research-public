"""Independent E057 state, stage-selection, source and null audit."""
from collections import Counter
import json
import math
from pathlib import Path
import random
import time
from verify_context_calibration import ContextVerifier,context_optimum,load,sha,to_indices,to_runes,tokenize,canonical
ROOT=Path(__file__).resolve().parents[1]


class BlindVerifier(ContextVerifier):
    def stream_row(self,cipher,row):
        self.coupled_row(cipher,self.page_spans,row)

    def result(self,cipher,result,page_spans):
        self.page_spans=page_spans
        starts_count=64 if len(cipher)<=1024 else 16
        retained=4 if len(cipher)<=1024 else 2
        assert result['starts_per_family']==starts_count and result['retained_per_family']==retained
        intervals=[]
        for span in page_spans:
            start,end=span['start'],span['end'];begin=start
            for i in range(start,end+1):
                if i==end or cipher[i]==0:
                    if i-begin>=16:intervals.append((begin,i))
                    begin=i+1
        ranges=[[a,min(b,a+256)] for a,b in sorted(intervals,key=lambda ab:(-(ab[1]-ab[0]),ab[0]))[:12]]
        pool=[];spans=[]
        for j,(a,b) in enumerate(ranges):
            start=len(pool);pool+=cipher[a:b]
            spans.append({'page_id':f'fragment-{j:02}','start':start,'end':len(pool),'runes':b-a,'zero_rune_page':False})
        assert pool==result['pool_ciphertext'] and spans==result['pool_spans'] and ranges==result['pool_source_ranges']
        assert 0 not in pool and len(result['unigram_starts'])==32*starts_count and len(result['families'])==32
        for row in result['unigram_starts']:
            assert 1<=row['unigram_steps']<=20
            self.pool_row(pool,spans,row)
        winners=[]
        for family in result['families']:
            m,sign=family['nominal_period'],family['sign'];assert 17<=m<=32 and sign in (1,-1)
            starts=[r for r in result['unigram_starts'] if r['nominal_period']==m and r['sign']==sign]
            assert [r['start'] for r in starts]==list(range(starts_count))
            unique={}
            for row in starts:
                ident=tuple(canonical(row['key']))
                if ident not in unique or row['score']>unique[ident]['score']:unique[ident]=row
            selected_starts=sorted(unique.values(),key=lambda r:r['score'],reverse=True)[:retained]
            assert [c['initial'] for c in family['candidates']]==selected_starts
            for candidate in family['candidates']:
                trace=candidate['pool_trace'];assert len(trace)==8
                assert [r['order'] for r in trace]==[2]*4+[4]*4
                for row in trace:self.pool_row(pool,spans,row)
                for a,b in zip(trace,trace[1:]):
                    if a['order']==b['order']:assert b['score']>=a['score']-1e-9
                assert candidate['state']==trace[-1] and candidate['nominal_period']==m
            winner=max(range(len(selected_starts)),key=lambda i:family['candidates'][i]['state']['score'])
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
        optimum=context_optimum(cipher,page_spans,best['key'],best['sign'],self.model)
        assert abs(optimum-best['language_score'])<1e-9
        self.counts['independent_coupled_optima']+=1
        self.check_alternatives(cipher,page_spans,best,result['alternatives'])

    def source(self,record,oracle_data):
        source=record['source'];index=record['index'];kind=record['kind'];truth=[]
        if kind in ('regression','stress'):
            expected=oracle_data['controls'][index if kind=='regression' else 12+index]['source']
            assert source==expected
        else:
            chapter=('X','XI','XII')[index];full=[];ranges=[]
            for r in self.rows:
                if r['chapter']!=chapter:continue
                a,b=r['source_character_range'];piece=[x for w in tokenize(self.raw[a:b])[0] for x in w]
                start=max(0,14000-len(full));end=min(len(piece),14729-len(full))
                if start<end:ranges.append({'source_character_range':[a,b],'paragraph':r['paragraph'],'paragraph_rune_range':[start,end]})
                full+=piece
                if len(full)>=14729:break
            truth=full[14000:14729];assert to_runes(truth)==source['truth_runes'] and source['source_ranges']==ranges
            assert source['chapter_rune_range']==[14000,14729]
            m=(17,23,31)[index];rng=random.Random(3301057+index);key=[rng.randrange(1,29) for _ in range(m)]
            phases=[0,rng.randrange(m),rng.randrange(m)];mask_rng=random.Random(3304057+index);prob=(.25,.5,.75)[index]
            skips=[i for i,c in enumerate(truth) if c==0 and mask_rng.random()<prob]
            assert source['injected_key']==key and source['injected_phases']==phases and source['injected_skips']==skips
            assert source['injected_sign']==(1,-1,1)[index] and source['F_copy_probability']==prob
            assert [(s['start'],s['end']) for s in source['page_spans']]==[(0,262),(262,528),(528,729)]
        if not truth:
            for r in source['source_ranges']:
                a,b=r['source_character_range'];piece=[x for w in tokenize(self.raw[a:b])[0] for x in w]
                start,end=r.get('paragraph_rune_range',[0,r.get('runes_consumed')]);truth+=piece[start:end]
        assert to_runes(truth)==source['truth_runes']
        for r in source['source_ranges']:
            a,b=r['source_character_range'];assert all(b<=x or a>=y for x,y in self.ranges)
        cipher=source['ciphertext_indices'];spans=source['page_spans']
        assert self.page_plain(cipher,spans,source['injected_key'],source['injected_sign'],source['injected_skips'],source['injected_phases'])==truth
        top=record['result']['top'][0];expected={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
            'key_exact':top['key']==source['injected_key'] and top['sign']==source['injected_sign'],
            'mask_exact':top['skip_positions']==source['injected_skips'],'phases_exact':top['page_phases']==source['injected_phases']}
        assert expected==record['checks'] and record['exact']==all(expected.values())
        assert record['correct_runes']==sum(a==b for a,b in zip(truth,to_indices(top['plaintext_runes'])))
        return truth


def verify():
    tick=time.perf_counter();events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    latest={e['output']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E057-')}
    complete=load('checkpoints/phase20_blind_complete.json');assert set(latest)==set(complete['outputs'])
    assert len(latest)==(19 if complete['stage_A_passed'] else 5)
    expected=[('regression',2)]+[('fresh',i) for i in range(3)]+[('null',2)]
    if complete['stage_A_passed']:expected += [('regression',i) for i in range(12) if i!=2]+[('stress',i) for i in range(3)]
    oracle_data=load(load('results/phase20_context_validation.json')['entry']['output']);v=BlindVerifier();controls=[];entries=[];data=[]
    for path,pair in zip(complete['outputs'],expected):
        assert time.perf_counter()-tick<300
        event=latest[path];assert event['wall_seconds']<180 and sha(path)==event['output_sha256']
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);data.append(row);assert (row['kind'],row['index'])==pair
        assert row['training']['training_source_ranges']==v.ranges
        assert row['unknown_sections_searched']==0 and row['new_decryptions']==[]
        source=row['source'];cipher=source['ciphertext_indices'];spans=source['page_spans']
        v.result(cipher,row['result'],spans)
        if row['kind']!='null':
            truth=v.source(row,oracle_data);m=len(source['injected_key']);G=sum(s['runes']>0 for s in spans)
            score=v.model.score(truth)-(m*math.log(29)+cipher.count(0)*math.log(2)+(G-1)*math.log(m))/len(cipher)
            controls.append({'kind':row['kind'],'index':row['index'],'runes':len(cipher),'key_length':m,
                'checks':row['checks'],'exact':row['exact'],'correct_runes':row['correct_runes'],
                'found_score':row['result']['top'][0]['score'],'truth_score':score,'output':path})
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        print({'verified':event['experiment'],**v.counts},flush=True)
    assert complete['stage_A_passed']==all(r['exact'] for r in data[:4])
    assert complete['stage_B_executed']==complete['stage_A_passed']
    assert complete['controls_completed']==len(controls) and complete['exact_controls']==sum(c['exact'] for c in controls)
    assert complete['full_gate_passed']==(len(controls)==18 and all(c['exact'] for c in controls))
    source=data[3]['source'];null=data[4]['source'];out=[];records=[];equal=lambda p:sum(a==b for a,b in zip(p,p[1:]))
    for j,s in enumerate(source['page_spans']):
        part=source['ciphertext_indices'][s['start']:s['end']];rng=random.Random(3302057+j)
        for n in range(1,100001):
            interior=part[1:-1];rng.shuffle(interior);sample=part[:1]+interior+part[-1:]
            if equal(sample)==equal(part):break
        else:raise AssertionError('Null rejection cap')
        assert Counter(sample)==Counter(part);out+=sample;records.append({'page_id':s['page_id'],'seed':3302057+j,'proposals':n})
    assert null['page_spans']==source['page_spans'] and out==null['ciphertext_indices'] and records==null['page_proposals']
    assert complete['null_score']==data[4]['result']['top'][0]['score']
    processes=load('results/phase20_blind_processes.json');assert all(p['exit_code']==0 and p['reason'] is None and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    summary={'experiment':'E057','stage_A_passed':complete['stage_A_passed'],'stage_B_executed':complete['stage_B_executed'],
        'full_gate_passed':complete['full_gate_passed'],'controls':controls,'null_score':complete['null_score'],
        'validation':dict(v.counts),'seconds':sum(e['wall_seconds'] for e in latest.values()),
        'successful_tasks':len(latest),'peak_sampled_bytes':max(p['peak_sampled_bytes'] for p in processes),
        'entries':entries,'unknown_sections_searched':0,'new_decryptions':[]}
    assert summary['seconds']<1400 and complete['seconds']+complete['prior_seconds']<1400
    (ROOT/'results/phase20_blind_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:x for k,x in summary.items() if k not in ('entries','controls')}),flush=True);return summary


if __name__=='__main__':verify()

