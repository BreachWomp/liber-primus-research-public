"""Independent branch evidence, hybrid union and fresh source verification."""
from collections import Counter
import json
import math
from pathlib import Path
import random
import time
from verify_constrained_fragments import ConstraintVerifier,load,sha,to_indices,to_runes,tokenize
from verify_context_blind import BlindVerifier
ROOT=Path(__file__).resolve().parents[1]


class HybridVerifier(BlindVerifier):
    def source(self,record,oracle_data):
        source=record['source'];index=record['index'];kind=record['kind'];truth=[]
        if kind in ('regression','stress'):
            expected=oracle_data[index]['source']
            assert source==expected
        else:
            chapter=('X','XI','XII')[index];full=[];ranges=[]
            for r in self.rows:
                if r['chapter']!=chapter:continue
                a,b=r['source_character_range'];piece=[x for w in tokenize(self.raw[a:b])[0] for x in w]
                start=max(0,16850-len(full));end=min(len(piece),17579-len(full))
                if start<end:ranges.append({'source_character_range':[a,b],'paragraph':r['paragraph'],'paragraph_rune_range':[start,end]})
                full+=piece
                if len(full)>=17579:break
            truth=full[16850:17579];assert to_runes(truth)==source['truth_runes'] and source['source_ranges']==ranges
            assert source['chapter_rune_range']==[16850,17579]
            m=(17,23,31)[index];rng=random.Random(3301060+index);key=[rng.randrange(1,29) for _ in range(m)]
            phases=[0,rng.randrange(m),rng.randrange(m)];mask_rng=random.Random(3304060+index);prob=(.25,.5,.75)[index]
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
    tick=time.perf_counter()
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    completed={e['output']:e for e in events if e['status']=='completed'}
    summary=load('checkpoints/phase21_hybrid_complete.json')
    prior=load('results/phase21_constraints_validation.json')
    originals=[load(c['output']) for c in prior['controls']]
    expected=[('regression',i) for i in (0,14)]+[('fresh',i) for i in range(3)]+[('null',2)]
    if summary['stage_A_passed']:expected += [('regression',i) for i in range(18) if i not in (0,14)]
    assert len(expected)==len(summary['outputs'])
    v=HybridVerifier();vc=ConstraintVerifier();vi=BlindVerifier();rows=[];controls=[];entries=[];cache_count=0
    admitted={name:{e['output']:e for e in load(path)['entries']} for name,path in
        (('constrained','results/phase21_constraints_validation.json'),('independent','results/phase20_blind_validation.json'))}
    def branch_result(record,name):
        nonlocal cache_count
        branch=record['result']['branches'][name]
        if 'result' in branch:
            found=branch['result']
            (vc if name=='constrained' else vi).result(record['source']['ciphertext_indices'],found,record['source']['page_spans'])
            return found
        path=branch['cached_output'];entry=admitted[name][path];event=completed[path]
        assert sha(path)==branch['cached_sha256']==entry['sha256']==event['output_sha256']
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        old=load(path)
        assert all(old['source'][k]==record['source'][k] for k in ('ciphertext_indices','page_spans'))
        assert old['training']==record['training']
        # Pinned prior independent validation establishes all branch internals.
        cache_count+=1
        return old['result']
    for path,pair in zip(summary['outputs'],expected):
        assert time.perf_counter()-tick<600
        event=completed[path];assert event['experiment'].startswith('E060-')
        assert sha(path)==event['output_sha256'] and event['wall_seconds']<180
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);rows.append(row);assert (row['kind'],row['index'])==pair
        assert row['training']['training_source_ranges']==v.ranges
        assert row['training']['source_sha256']==sha('data/raw/gutenberg/pg2944.txt')
        source=row['source'];cipher=source['ciphertext_indices'];spans=source['page_spans']
        candidates=[]
        for name in ('constrained','independent'):candidates+=branch_result(row,name)['top']
        ranked=[];seen=set()
        for candidate in sorted(candidates,key=lambda r:r['score'],reverse=True):
            if candidate['plaintext_runes'] not in seen:
                ranked.append(candidate);seen.add(candidate['plaintext_runes'])
        assert row['result']['top']==ranked[:3]
        for candidate in ranked[:3]:vc.coupled_row(cipher,spans,candidate)
        vc.check_alternatives(cipher,spans,ranked[0],row['result']['alternatives'])
        if row['kind']!='null':
            truth=v.source(row,originals);m=len(source['injected_key']);G=sum(s['runes']>0 for s in spans)
            score=v.model.score(truth)-(m*math.log(29)+cipher.count(0)*math.log(2)+(G-1)*math.log(m))/len(cipher)
            controls.append({'kind':row['kind'],'index':row['index'],'runes':len(cipher),'key_length':m,
                'exact':row['exact'],'checks':row['checks'],'correct_runes':row['correct_runes'],
                'found_score':ranked[0]['score'],'truth_score':score,'output':path})
        assert row['unknown_sections_searched']==0 and row['new_decryptions']==[]
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        print({'verified':event['experiment'],'cached_branches':cache_count},flush=True)
    assert summary['stage_A_passed']==all(r['exact'] for r in rows[:5])
    assert summary['stage_B_executed']==summary['stage_A_passed']
    assert summary['full_gate_passed']==(len(controls)==21 and all(r['exact'] for r in controls))
    assert summary['controls_completed']==len(controls) and summary['exact_controls']==sum(r['exact'] for r in controls)
    source=rows[4]['source'];null=rows[5]['source'];out=[];proposals=[]
    equal=lambda p:sum(a==b for a,b in zip(p,p[1:]))
    for j,s in enumerate(source['page_spans']):
        part=source['ciphertext_indices'][s['start']:s['end']];rng=random.Random(3302060+j)
        for n in range(1,100001):
            middle=part[1:-1];rng.shuffle(middle);sample=part[:1]+middle+part[-1:]
            if equal(sample)==equal(part):break
        else:raise AssertionError('Null rejection cap')
        assert Counter(sample)==Counter(part);out+=sample
        proposals.append({'page_id':s['page_id'],'seed':3302060+j,'proposals':n})
    assert null['ciphertext_indices']==out and null['page_proposals']==proposals and null['page_spans']==source['page_spans']
    assert summary['null_score']==rows[5]['result']['top'][0]['score']
    processes=load('results/phase21_hybrid_processes.json')
    assert all(p['exit_code']==0 and p['reason'] is None and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    counts=Counter(vc.counts);counts.update(vi.counts)
    counts['pinned_previously_validated_branches']=cache_count
    result={'experiment':'E060','stage_A_passed':summary['stage_A_passed'],'stage_B_executed':summary['stage_B_executed'],
        'full_gate_passed':summary['full_gate_passed'],'controls':controls,'null_score':summary['null_score'],
        'validation':dict(counts),'seconds':sum(completed[e['output']]['wall_seconds'] for e in entries),
        'successful_tasks':len(entries),'peak_sampled_bytes':max(p['peak_sampled_bytes'] for p in processes),
        'entries':entries,'unknown_sections_searched':0,'new_decryptions':[]}
    assert result['seconds']<1800 and summary['seconds']+summary['prior_seconds']<1800
    (ROOT/'results/phase21_hybrid_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:x for k,x in result.items() if k not in ('entries','controls')}),flush=True)


if __name__=='__main__':verify()

