"""Independent page-boundary/source replay and long-key phase validation."""
from collections import Counter
import json
import math
from pathlib import Path
import random
import time
from verify_phase18 import Verifier,load,sha,to_indices,to_runes,tokenize
from finalize_phase17 import scalar_replay,schedule_optimum,canonical
ROOT=Path(__file__).resolve().parents[1]


class PageVerifier(Verifier):
    def page_plain(self,cipher,spans,key,sign,skips,phases):
        assert len(phases)==len(spans) and phases[next(i for i,s in enumerate(spans) if s['runes'])]==0
        out=[]
        for span,phase in zip(spans,phases):
            a,b=span['start'],span['end'];assert 0<=phase<len(key)
            if a==b:assert phase==0;continue
            out+=scalar_replay(cipher[a:b],key[phase:]+key[:phase],sign,[i-a for i in skips if a<=i<b])
        return out

    def stream_row(self,cipher,row):
        spans=self.page_spans;key=row['key'];assert 1<=len(key)<=32 and len(canonical(key))==len(key)
        assert row['skip_positions']==sorted(set(row['skip_positions']))
        plain=self.page_plain(cipher,spans,key,row['sign'],row['skip_positions'],row['page_phases'])
        language=sum(self.language(plain[s['start']:s['end']],4) for s in spans if s['runes'])/len(cipher)
        phase_cost=(sum(s['runes']>0 for s in spans)-1)*math.log(len(key))
        assert abs(language-row['language_score'])<1e-9
        assert abs(phase_cost-row['phase_cost'])<1e-9
        assert abs(language-(len(key)*math.log(29)+cipher.count(0)*math.log(2)+phase_cost)/len(cipher)-row['score'])<1e-9
        assert row['dp_max_states']<=8*row['input_period'] and row['input_period']<=32
        assert 0<=row['rotation']<row['input_period']
        if 'plaintext_runes' in row:assert to_runes(plain)==row['plaintext_runes']
        self.counts['stream_records_recomputed']+=1

    def result(self,cipher,result,page_spans):
        self.page_spans=page_spans
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
        optimum=sum((s['end']-s['start'])*schedule_optimum(cipher[s['start']:s['end']],best['key'],best['sign'],self.model) for s in page_spans if s['end']>s['start'])/len(cipher)
        assert abs(optimum-best['language_score'])<1e-9
        self.counts['independent_stream_optima']+=1

    def check_source(self,row):
        source=row['source'];kind=row['kind'];index=row['index'];plain=[]
        assert row['training']['training_source_ranges']==self.ranges
        assert row['training']['source_sha256']==sha('data/raw/gutenberg/pg2944.txt')
        for r in source['source_ranges']:
            a,b=r['source_character_range'];piece=[x for w in tokenize(self.raw[a:b])[0] for x in w]
            assert all(b<=x or a>=y for x,y in self.ranges)
            start,end=r.get('paragraph_rune_range',[0,r.get('runes_consumed')]);plain+=piece[start:end]
        assert to_runes(plain)==source['truth_runes']
        spans=source['page_spans']
        if kind=='fresh':
            chapter=('X','XI','XII')[index%3];m=(17,23,31)[index%3];sign=(1,-1,1)[index%3]
            offset=6000 if index<3 else 8000;length=729 if index<3 else 3316
            all_runes=[];expected=[]
            for r in self.rows:
                if r['chapter']!=chapter:continue
                a,b=r['source_character_range'];piece=[x for w in tokenize(self.raw[a:b])[0] for x in w]
                start=max(0,offset-len(all_runes));end=min(len(piece),offset+length-len(all_runes))
                if start<end:expected.append({'source_character_range':[a,b],'paragraph':r['paragraph'],'paragraph_rune_range':[start,end]})
                all_runes+=piece
                if len(all_runes)>=offset+length:break
            assert plain==all_runes[offset:offset+length] and source['source_ranges']==expected
            assert source['chapter_rune_range']==[offset,offset+length]
            ids=[f'LP2-{i:02}' for i in (range(3) if index<3 else range(40,56))]
            catalog={p['id']:p for p in load('transcriptions/pages.json')};expected_spans=[];cursor=0
            for j,ident in enumerate(ids):
                n=len(to_indices(catalog[ident]['runes']))
                expected_spans.append({'page_id':f'external-{chapter}-{j:02}','start':cursor,'end':cursor+n,'runes':n,'zero_rune_page':n==0});cursor+=n
            assert ids==source['source_span_page_ids'] and spans==expected_spans
            rng=random.Random(3301054+index);key=[rng.randrange(1,29) for _ in range(m)]
            phases=[];first=True
            for s in spans:
                phases.append(0 if not s['runes'] or first else rng.randrange(m))
                if s['runes']:first=False
            prob=(.25,.5,.75)[index%3];mask_rng=random.Random(3304054+index)
            skips=[i for i,c in enumerate(plain) if c==0 and mask_rng.random()<prob]
            assert source['F_copy_probability']==prob
        else:
            old=load(source['regression_output'])['source']
            assert {k:v for k,v in source.items() if k not in ('injected_phases','regression_output')}==old
            key=old['injected_key'];sign=old['injected_sign'];skips=old['injected_skips'];phases=[];cursor=0
            for s in spans:
                phases.append(cursor%len(key) if s['runes'] else 0)
                cursor+=s['runes']-sum(s['start']<=i<s['end'] for i in skips)
        assert key==source['injected_key'] and sign==source['injected_sign']
        assert phases==source['injected_phases'] and skips==source['injected_skips']
        assert self.page_plain(source['ciphertext_indices'],spans,key,sign,skips,phases)==plain
        top=row['result']['top'][0]
        expected={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
            'key_exact':top['key']==key and top['sign']==sign,'mask_exact':top['skip_positions']==skips,
            'phases_exact':top['page_phases']==phases}
        assert row['checks']==expected and row['exact']==all(expected.values())
        assert row['correct_runes']==sum(a==b for a,b in zip(plain,to_indices(top['plaintext_runes'])))
        return plain


def verify():
    tick=time.perf_counter();events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    latest={e['experiment']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E054-')}
    assert len(latest)==13;v=PageVerifier();controls=[];data={};entries=[]
    for ident,event in latest.items():
        assert time.perf_counter()-tick<300 and event['wall_seconds']<180
        assert sha(event['output'])==event['output_sha256']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
        row=load(event['output']);source=row['source'];data[ident]=row
        assert row['unknown_sections_searched']==0 and row['new_decryptions']==[]
        v.result(source['ciphertext_indices'],row['result'],source['page_spans'])
        if row['kind']!='null':
            plain=v.check_source(row);top=row['result']['top'][0];m=len(source['injected_key']);spans=source['page_spans']
            language=sum(v.language(plain[s['start']:s['end']],4) for s in spans if s['runes'])/len(plain)
            truth=language-(m*math.log(29)+source['ciphertext_indices'].count(0)*math.log(2)+(sum(s['runes']>0 for s in spans)-1)*math.log(m))/len(plain)
            errors=[i for i,(a,b) in enumerate(zip(plain,to_indices(top['plaintext_runes']))) if a!=b]
            controls.append({'kind':row['kind'],'index':row['index'],'chapter':source['chapter'],'key_length':m,
                'runes':len(plain),'exact':row['exact'],'checks':row['checks'],'correct_runes':row['correct_runes'],
                'found_score':top['score'],'truth_score':truth,'truth_minus_found':truth-top['score'],
                'error_positions':errors,'page_start_errors':[i for i in errors if i in [s['start'] for s in spans if s['runes']]],
                'output':event['output']})
        entries.append({'id':ident,'fingerprint':event['fingerprint'],'output':event['output'],'sha256':event['output_sha256']})
        print({'verified':ident,**v.counts},flush=True)
    source=data['E054-fresh-2']['source'];null=data['E054-null-2']['source'];out=[];records=[]
    doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]))
    for j,span in enumerate(source['page_spans']):
        part=source['ciphertext_indices'][span['start']:span['end']];rng=random.Random(3302054+j)
        for proposals in range(1,100001):
            middle=part[1:-1];rng.shuffle(middle);sample=part[:1]+middle+part[-1:]
            if doublets(sample)==doublets(part):break
        else:raise AssertionError('Null rejection cap')
        assert Counter(sample)==Counter(part);out+=sample
        records.append({'page_id':span['page_id'],'seed':3302054+j,'proposals':proposals})
    assert source['page_spans']==null['page_spans'] and out==null['ciphertext_indices'] and records==null['page_proposals']
    processes=load('results/phase19_processes.json');assert len(processes)==13
    assert all(p['exit_code']==0 and p['reason'] is None and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    summary={'experiment':'E054','gate_passed':all(r['exact'] for r in controls),'controls':controls,
             'null_score':data['E054-null-2']['result']['top'][0]['score'],
             'seconds':sum(e['wall_seconds'] for e in latest.values()),'successful_tasks':13,
             'peak_sampled_bytes':max(p['peak_sampled_bytes'] for p in processes),
             'validation':dict(v.counts),'entries':entries,'new_decryptions':[]}
    assert summary['seconds']<1200
    (ROOT/'results/phase19_control_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:x for k,x in summary.items() if k not in ('controls','entries')}),flush=True)
    return summary


if __name__=='__main__':verify()

