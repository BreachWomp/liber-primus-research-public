"""Independent long-control source, continuous queue and per-page null replay."""
from collections import Counter,deque
import json
import random
import time
from verify_autokey_extended import ROOT,load,sha,Verifier,to_indices,tokenize


class SectionVerifier(Verifier):
    def spans(self,group):
        catalog={p['id']:p for p in load('transcriptions/pages.json')};cipher=[];spans=[]
        for ident in group['page_ids']:
            page=catalog[ident];piece=to_indices(page['runes']);start=len(cipher);cipher+=piece
            spans.append({'page_id':ident,'start':start,'end':len(cipher),'runes':len(piece),
                'source_refs':page['source_refs'],'zero_rune_page':not bool(piece)})
        return cipher,spans

    def source(self,index,source):
        chapter=('X','XI','XII','X')[index];start=1000 if index<3 else 5400;n=3316
        m=(13,23,31,32)[index];raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
        plain=[];ranges=[];cursor=0
        for row in self.rows:
            if row['chapter']!=chapter:continue
            a,b=row['source_character_range'];words,_,_=tokenize(raw[a:b]);piece=[x for w in words for x in w]
            low=max(0,start-cursor);high=min(len(piece),start+n-cursor)
            if low<high:
                plain+=piece[low:high];ranges.append({'source_character_range':[a,b],'paragraph':row['paragraph'],'paragraph_rune_range':[low,high]})
            cursor+=len(piece)
            if cursor>=start+n:break
        rng=random.Random(3301064+index);key=[rng.randrange(29) for _ in range(m)]
        cs,ks=((1,-1),(1,1),(-1,-1),(-1,1))[index];queue=deque(key);cipher=[]
        for p in plain:cipher.append(cs*(p-ks*queue.popleft())%29);queue.append(p)
        assert len(plain)==n and to_indices(source['truth_runes'])==plain
        assert source['source_ranges']==ranges and source['chapter']==chapter and source['chapter_rune_range']==[start,start+n]
        assert source['injected_key']==key and source['cipher_sign']==cs and source['feedback_sign']==ks and source['ciphertext_indices']==cipher
        group=next(g for g in load('experiments/section_plan.json')['sections'] if g['id']=='LP2-40_55');_,template=self.spans(group)
        expected=[];cursor=0
        for i,s in enumerate(template):
            expected.append({'page_id':f'external-{chapter}-{i:02}','start':cursor,'end':cursor+s['runes'],'runes':s['runes'],'zero_rune_page':s['runes']==0});cursor+=s['runes']
        assert source['page_spans']==expected and cursor==3316 and sum(s['zero_rune_page'] for s in expected)==1

    def null(self,original,spans,seed):
        output=[];records=[];doublets=lambda a:sum(x==y for x,y in zip(a,a[1:]))
        for j,s in enumerate(spans):
            assert s['start']==len(output);piece=original[s['start']:s['end']]
            if len(piece)<=2:sample=piece[:];proposals=0
            else:
                rng=random.Random(seed+j)
                for proposals in range(1,100001):
                    middle=piece[1:-1];rng.shuffle(middle);sample=piece[:1]+middle+piece[-1:]
                    if doublets(sample)==doublets(piece):break
                else:raise AssertionError('Rejection cap')
                assert sample[0]==piece[0] and sample[-1]==piece[-1]
            assert Counter(sample)==Counter(piece)
            output+=sample;records.append({'page_id':s['page_id'],'seed':seed+j,'proposals':proposals})
        assert len(output)==len(original) and doublets(output)==doublets(original)
        return output,records

    def continuous(self,cipher,spans,result):
        for top in result['top']:
            r=top['recipe'];queue=deque(r['key_indices']);plain=[]
            for s in spans:
                assert s['start']==len(plain);before=list(queue)
                for c in cipher[s['start']:s['end']]:
                    p=(r['cipher_sign']*c+r['feedback_sign']*queue.popleft())%29
                    queue.append(p);plain.append(p)
                assert len(plain)==s['end']
                if s['zero_rune_page']:assert list(queue)==before
            assert plain==to_indices(top['plaintext_runes']);self.counts['continuous_page_queue_replays']+=1


def main():
    tick=time.perf_counter();complete=load('checkpoints/phase23_controls_complete.json');v=SectionVerifier();entries=[];controls=[]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    by_output={e['output']:e for e in events if e['status']=='completed'}
    prior=load('results/phase22_controls_validation.json');assert prior['full_gate_passed'] and len(prior['controls'])==12
    reused=[]
    for c in prior['controls']:
        event=by_output[c['output']];assert sha(c['output'])==event['output_sha256'] and c['exact']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
        old=load(c['output']);assert old['training']==v.training and old['exact']
        reused.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':c['output'],'sha256':event['output_sha256']})
    assert len(complete['outputs'])==5
    for path in complete['outputs']:
        assert time.perf_counter()-tick<900
        event=by_output[path];assert sha(path)==event['output_sha256'] and event['wall_seconds']<180
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);assert row['training']==v.training;source=row['source']
        if row['kind']=='control':v.source(row['index'],source)
        else:
            original=load(next(p for p in complete['outputs'] if load(p)['kind']=='control' and load(p)['index']==3))['source']
            assert source['page_spans']==original['page_spans']
            sample,records=v.null(original['ciphertext_indices'],source['page_spans'],3302064)
            assert sample==source['ciphertext_indices'] and records==source['page_proposals']
        v.result(source['ciphertext_indices'],row['result']);v.continuous(source['ciphertext_indices'],source['page_spans'],row['result'])
        if row['kind']=='control':
            top=row['result']['top'][0];r=top['recipe'];exact=top['plaintext_runes']==source['truth_runes']
            exact_recipe=r['key_indices']==source['injected_key'] and r['cipher_sign']==source['cipher_sign'] and r['feedback_sign']==source['feedback_sign']
            assert row['exact']==exact and row['injected_recipe_exact']==exact_recipe
            assert row['correct_runes']==sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
            controls.append({'index':row['index'],'runes':3316,'key_length':len(source['injected_key']),'exact':exact,'injected_recipe_exact':exact_recipe,'output':path})
        else:null_score=row['result']['top'][0]['score']
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        print({'verified':event['experiment'],**v.counts},flush=True)
    assert [c['index'] for c in controls]==list(range(4))
    gate=all(c['exact'] and c['injected_recipe_exact'] for c in controls)
    assert complete['full_gate_passed']==gate and complete['null_score']==null_score
    processes=load('results/phase23_controls_processes.json');assert len(processes)==5
    assert all(r['exit_code']==0 and r['reason'] is None and r['peak_sampled_bytes']<=768*1024**2 for r in processes)
    assert complete['prior_seconds']+complete['seconds']<900
    summary={'full_gate_passed':gate,'controls':controls,'reused_control_entries':reused,'prior_validation_sha256':sha('results/phase22_controls_validation.json'),
        'null_score':null_score,'entries':entries,'validation':dict(v.counts),'seconds':sum(by_output[e['output']]['wall_seconds'] for e in entries),
        'peak_sampled_bytes':max(r['peak_sampled_bytes'] for r in processes),'validation_seconds':time.perf_counter()-tick,'new_decryptions':[]}
    (ROOT/'results/phase23_controls_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in summary.items() if k not in ('entries','controls','reused_control_entries')},flush=True)


if __name__=='__main__':main()
