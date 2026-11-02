"""Scalar replay and independent score-only transfer DP for E056."""
from collections import Counter
import json
import math
from pathlib import Path
import random
from verify_phase19 import PageVerifier,load,sha,to_indices,to_runes,tokenize,canonical
ROOT=Path(__file__).resolve().parents[1]


def context_optimum(cipher,spans,key,sign,model):
    prefixes={():0.}
    for span in spans:
        a,b=span['start'],span['end']
        if a==b:continue
        active={(p,h):score for h,score in prefixes.items() for p in range(len(key))}
        for c in cipher[a:b]:
            next_states={}
            for (p,h),score in active.items():
                choices=[((sign*c+key[p])%29,(p+1)%len(key))]
                if c==0:choices.append((0,p))
                for symbol,q in choices:
                    nh=(h+(symbol,))[-3:];index=(q,nh);value=score+model.logp(h,symbol)
                    if value>next_states.get(index,-float('inf')):next_states[index]=value
            active=next_states
        prefixes={}
        for (_,h),score in active.items():prefixes[h]=max(prefixes.get(h,-float('inf')),score)
    return max(prefixes.values())/len(cipher)


class ContextVerifier(PageVerifier):
    def coupled_row(self,cipher,spans,row,optimum=False):
        key=row['key'];assert 1<=len(key)<=32 and len(canonical(key))==len(key)
        plain=self.page_plain(cipher,spans,key,row['sign'],row['skip_positions'],row['page_phases'])
        language=self.model.score(plain);phase_cost=(sum(s['runes']>0 for s in spans)-1)*math.log(len(key))
        score=language-(len(key)*math.log(29)+cipher.count(0)*math.log(2)+phase_cost)/len(cipher)
        assert abs(language-row['language_score'])<1e-9 and abs(score-row['score'])<1e-9
        assert abs(row['phase_cost']-phase_cost)<1e-9 and row['dp_max_states']<=16*row['input_period']**2
        assert 0<=row['rotation']<row['input_period']<=32
        assert len(row['boundary_context_counts'])==len(spans)
        if 'plaintext_runes' in row:assert to_runes(plain)==row['plaintext_runes']
        if optimum:
            assert abs(context_optimum(cipher,spans,key,row['sign'],self.model)-language)<1e-9
            self.counts['independent_coupled_optima']+=1
        self.counts['coupled_records_recomputed']+=1
        return plain

    def check_alternatives(self,cipher,spans,row,alternatives):
        first=next(i for i,s in enumerate(spans) if s['runes']);expected=[(j,s['start']) for j,s in enumerate(spans) if s['runes'] and j!=first and cipher[s['start']]==0]
        assert [(a['page_index'],a['position']) for a in alternatives]==expected
        baseline=self.page_plain(cipher,spans,row['key'],row['sign'],row['skip_positions'],row['page_phases'])
        m=len(row['key']);penalty=(m*math.log(29)+cipher.count(0)*math.log(2)+(sum(s['runes']>0 for s in spans)-1)*math.log(m))/len(cipher)
        for alt in alternatives:
            a=alt['position'];j=alt['page_index'];phases=row['page_phases'][:]
            phases[j]=(phases[j]+(-1 if a in row['skip_positions'] else 1))%m
            assert alt['page_phases']==phases and alt['skip_positions']==sorted(set(row['skip_positions'])^{a})
            assert alt['key']==row['key'] and alt['sign']==row['sign']
            plain=self.page_plain(cipher,spans,alt['key'],alt['sign'],alt['skip_positions'],phases)
            assert alt['changed_positions']==[i for i,(x,y) in enumerate(zip(plain,baseline)) if x!=y]
            assert alt['changed_positions'] in ([],[a]) and alt['ciphertext_identical']
            assert to_runes(plain)==alt['plaintext_runes'] and abs(self.model.score(plain)-penalty-alt['score'])<1e-9
            self.counts['alternative_pairs_recomputed']+=1


def verify():
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    event=next(e for e in reversed(events) if e['experiment']=='E056-context-coupled-calibration' and e['status']=='completed')
    assert sha(event['output'])==event['output_sha256'] and event['wall_seconds']<180
    for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    data=load(event['output']);assert len(data['controls'])==15 and len(data['nulls'])==1 and not data['blind_gate_passed']
    v=ContextVerifier();assert data['training']['training_source_ranges']==v.ranges
    old=load('results/phase19_control_validation.json');diagnosis=load('results/E055-long-page-phase-diagnosis-29c3d4f36f52.json')
    oracle={r['control_output']:r['known_key_oracle']['result'] for r in diagnosis['controls'] if 'known_key_oracle' in r}
    old_entries=[e for e in old['entries'] if 'null' not in e['id']];rows=[]
    for i,record in enumerate(data['controls']):
        source=record['source'];cipher=source['ciphertext_indices'];spans=source['page_spans'];truth=[]
        if record['kind']=='regression':
            path=old_entries[i]['output'];prior=load(path)
            assert source==prior['source'] and record['source_output']==path and record['baseline_reused']
            assert record['reset']==oracle.get(path,prior['result']['top'][0])
        else:
            index=record['index'];chapter=('X','XI','XII')[index];full=[];ranges=[]
            for r in v.rows:
                if r['chapter']!=chapter:continue
                a,b=r['source_character_range'];piece=[x for w in tokenize(v.raw[a:b])[0] for x in w]
                start=max(0,12000-len(full));end=min(len(piece),12729-len(full))
                if start<end:ranges.append({'source_character_range':[a,b],'paragraph':r['paragraph'],'paragraph_rune_range':[start,end]})
                full+=piece
                if len(full)>=12729:break
            truth=full[12000:12729];assert to_runes(truth)==source['truth_runes'] and source['source_ranges']==ranges
            assert source['chapter_rune_range']==[12000,12729] and not record['baseline_reused'] and record['source_output'] is None
            boundary=next(i for i in range(262,294) if truth[i]!=0);assert boundary==source['stress_boundary']
            assert [(s['start'],s['end']) for s in spans]==[(0,boundary),(boundary,528),(528,729)]
            m=(17,23,31)[index];rng=random.Random(3301056+index);key=[rng.randrange(1,29) for _ in range(m)];key[0]=truth[boundary]
            phases=[0,0,rng.randrange(m)];mask_rng=random.Random(3304056+index);prob=(.25,.5,.75)[index]
            skips=[i for i,c in enumerate(truth) if c==0 and mask_rng.random()<prob]
            assert source['injected_key']==key and source['injected_phases']==phases and source['injected_skips']==skips
            assert source['injected_sign']==(1,-1,1)[index] and source['F_copy_probability']==prob
        if not truth:
            for r in source['source_ranges']:
                a,b=r['source_character_range'];piece=[x for w in tokenize(v.raw[a:b])[0] for x in w]
                start,end=r.get('paragraph_rune_range',[0,r.get('runes_consumed')]);truth+=piece[start:end]
        assert to_runes(truth)==source['truth_runes']
        for r in source['source_ranges']:
            a,b=r['source_character_range'];assert all(b<=x or a>=y for x,y in v.ranges)
        assert v.page_plain(cipher,spans,source['injected_key'],source['injected_sign'],source['injected_skips'],source['injected_phases'])==truth
        assert record['truth_inputs']==['injected_key_cycle','injected_sign']
        v.page_spans=spans;v.stream_row(cipher,record['reset']);v.coupled_row(cipher,spans,record['coupled'],optimum=True)
        for mode in ('reset','coupled'):
            candidate=record[mode];expected={'plaintext_exact':candidate['plaintext_runes']==source['truth_runes'],
                'key_exact':candidate['key']==source['injected_key'] and candidate['sign']==source['injected_sign'],
                'mask_exact':candidate['skip_positions']==source['injected_skips'],'phases_exact':candidate['page_phases']==source['injected_phases']}
            assert record[mode+'_checks']==expected
        assert record['coupled_exact']==all(record['coupled_checks'].values())
        v.check_alternatives(cipher,spans,record['coupled'],record['alternatives'])
        rows.append({'kind':record['kind'],'index':record['index'],'runes':len(cipher),'key_length':len(source['injected_key']),
            'reset_exact':all(record['reset_checks'].values()),'coupled_exact':record['coupled_exact'],
            'coupled_correct_runes':sum(a==b for a,b in zip(truth,to_indices(record['coupled']['plaintext_runes']))),
            'alternatives':len(record['alternatives']),'dp_max_states':record['coupled']['dp_max_states']})
    null=data['nulls'][0];source=data['controls'][-1]['source'];out=[];proposals=[];equal=lambda p:sum(a==b for a,b in zip(p,p[1:]))
    for j,s in enumerate(source['page_spans']):
        part=source['ciphertext_indices'][s['start']:s['end']];rng=random.Random(3302056+j)
        for n in range(1,100001):
            interior=part[1:-1];rng.shuffle(interior);sample=part[:1]+interior+part[-1:]
            if equal(sample)==equal(part):break
        else:raise AssertionError('Null rejection cap')
        assert Counter(sample)==Counter(part);out+=sample;proposals.append({'page_id':s['page_id'],'seed':3302056+j,'proposals':n})
    assert out==null['ciphertext_indices'] and proposals==null['page_proposals'] and source['page_spans']==null['page_spans']
    v.page_spans=null['page_spans'];v.stream_row(out,null['reset']);v.coupled_row(out,null['page_spans'],null['coupled'],optimum=True)
    assert all(canonical(null[k]['key'])==canonical(source['injected_key']) and null[k]['sign']==source['injected_sign'] for k in ('reset','coupled'))
    process=load('results/phase20_context_processes.json')[0];assert process['exit_code']==0 and process['reason'] is None and process['peak_sampled_bytes']<768*1024**2
    assert data['oracle_gate_passed']==all(r['coupled_exact'] for r in rows)
    summary={'experiment':'E056','oracle_gate_passed':data['oracle_gate_passed'],'blind_gate_passed':False,
        'controls':rows,'validation':dict(v.counts),'seconds':event['wall_seconds'],'peak_sampled_bytes':process['peak_sampled_bytes'],
        'entry':{'id':event['experiment'],'fingerprint':event['fingerprint'],'output':event['output'],'sha256':event['output_sha256']},
        'unknown_sections_searched':0,'new_decryptions':[]}
    (ROOT/'results/phase20_context_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary),flush=True);return summary


if __name__=='__main__':verify()
