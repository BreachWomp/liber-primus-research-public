"""Independent E073 source spans, continuous queues, nulls and selection audit."""
from collections import deque
import hashlib
import json
import time
from verify_affine_feedback import ROOT,load,sha,AffineVerifier,to_indices
from verify_autokey_sections import SectionVerifier
from liberprimus.alphabet import RUNES

class CombinedVerifier(AffineVerifier,SectionVerifier):
    def source_anchors(self):
        manifest={r['id']:r for r in load('sources/manifest.json')['files']}
        checked={};anchors=[]
        for page in load('transcriptions/pages.json'):
            if page['edition']!='LP2' or page['page']>55:continue
            for ref in page['source_refs']:
                r=manifest[ref]
                assert sha(r['local_path'])==r['sha256'] and len(r['commit'])==40 and r['retrieved_at_utc']
                checked[r['local_path']]=r['sha256']
            primary=next(ref for ref in page['source_refs'] if ref.startswith('relikd:'))
            raw=(ROOT/manifest[primary]['local_path']).read_text(encoding='utf-8')
            text=page['text_with_layout'];offset=raw.index(text)
            aliases={'ᛂ':'ᛄ'};unknown={x for x in text if 0x16a0<=ord(x)<=0x16ff and x not in RUNES and x not in aliases and x not in '᛫᛬᛭'}
            assert not unknown,(page['id'],unknown)
            runes=''.join(aliases.get(x,x) for x in text if aliases.get(x,x) in RUNES)
            assert runes==page['runes'] and len(runes)==page['rune_count']
            assert hashlib.sha256(runes.encode('utf-8')).hexdigest()==page['runes_sha256']
            anchors.append({'page_id':page['id'],'source':primary,'decoded_text_offset':offset,
                'decoded_text_length':len(text),'runes_sha256':page['runes_sha256']})
        assert len(anchors)==56 and len(checked)==10
        self.counts['literal_source_page_anchors']=len(anchors)
        self.counts['pinned_source_file_hashes']=len(checked)
        return {'files':checked,'pages':anchors,'manifest_sha256':sha('sources/manifest.json'),
            'note':'Literal layout substring in decoded source; text offsets are character offsets after universal newline reading, not byte offsets. Raw bytes verified separately; only declared alias ᛂ to ᛄ.'}

    def continuous(self,cipher,spans,result):
        for top in result['top']:
            r=top['recipe'];queue=deque(r['key_indices']);plain=[]
            for span in spans:
                assert span['start']==len(plain);before=list(queue)
                for x in cipher[span['start']:span['end']]:
                    p=(r['cipher_sign']*x+r['feedback_sign']*queue.popleft()+r['constant'])%29
                    queue.append(p);plain.append(p)
                assert len(plain)==span['end']
                if span['zero_rune_page']:assert list(queue)==before
            assert plain==to_indices(top['plaintext_runes'])
            self.counts['continuous_page_queue_replays']+=1


def main():
    tick=time.perf_counter();v=CombinedVerifier();plan=load('experiments/affine_feedback_unknown_plan.json')
    source_anchors=v.source_anchors()
    complete=load('checkpoints/phase26_unknown_complete.json');selection=load('experiments/affine_feedback_selection.json')
    assert sha('experiments/affine_feedback_selection.json')==complete['selection_sha256']
    assert load(plan['control_validation'])['full_gate_passed']
    groups={g['id']:g for g in plan['groups']}
    assert list(groups)==plan['section_ids'] and len(groups)==56
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    latest={e['output']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E073-')}
    assert set(latest)==set(complete['outputs']) and len(latest)==75
    entries=[];sections=[];nulls=[];coverage=set();empty=set()
    for path in complete['outputs']:
        assert time.perf_counter()-tick<2400
        event=latest[path];assert sha(path)==event['output_sha256'] and event['wall_seconds']<180
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);assert row['parameters']==plan and row['training']==v.training
        group=groups[row['section']];assert row['group']==group
        original,spans=v.spans(group);assert row['page_spans']==spans and 200<=len(original)<=3316
        if row['mode']=='section':
            assert row['replicate']==0 and row['page_proposals'] is None and row['ciphertext_indices']==original
            coverage.update(s['page_id'] for s in spans if s['runes']);empty.update(s['page_id'] for s in spans if not s['runes'])
        else:
            assert row['mode']=='null' and row['section']==selection['section'] and 0<=row['replicate']<19
            sample,proposals=v.null(original,spans,plan['null_seed']+100*row['replicate'])
            assert sample==row['ciphertext_indices'] and proposals==row['page_proposals']
        v.coefficients.clear();v.windows.clear()
        v.result(row['ciphertext_indices'],row['result']);v.continuous(row['ciphertext_indices'],spans,row['result'])
        top=row['result']['top'][0];compact={'section':row['section'],'replicate':row['replicate'],'runes':len(original),
            'score':top['score'],'key_length':len(top['recipe']['key_indices']),'cipher_sign':top['recipe']['cipher_sign'],'feedback_sign':top['recipe']['feedback_sign'],'constant':top['recipe']['constant'],'output':path}
        (sections if row['mode']=='section' else nulls).append(compact)
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        assert row['new_decryptions']==[];print({'verified':event['experiment'],'seconds':time.perf_counter()-tick},flush=True)
    assert [r['section'] for r in sections]==plan['section_ids'] and [r['replicate'] for r in nulls]==list(range(19))
    winner=max(sections,key=lambda r:r['score'])
    assert selection['section']==winner['section']==complete['section'] and selection['score']==winner['score']==complete['score']
    assert selection['source_outputs']=={r['output']:sha(r['output']) for r in sections}
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(1+exceed)/20
    assert complete['exceedances']==exceed and complete['raw_p']==p and complete['bonferroni56']==min(1,56*p)
    assert complete['pending_larger_calibration']==(exceed==0)
    assert len(coverage)==55 and empty=={'LP2-50'}
    processes=load('results/phase26_unknown_processes.json')
    assert len(processes)==75 and all(r['exit_code']==0 and r['reason'] is None and r['peak_sampled_bytes']<=768*1024**2 for r in processes)
    assert complete['seconds']+complete['prior_seconds']<plan['family_seconds']
    summary={'sections':sections,'nulls':nulls,'selected_section':winner['section'],'score':winner['score'],
        'exceedances':exceed,'raw_p':p,'bonferroni56':min(1,56*p),'pending_larger_calibration':exceed==0,
        'unique_unknown_rune_pages':len(coverage),'empty_pages_preserved':sorted(empty),'entries':entries,'validation':dict(v.counts),
        'seconds':sum(e['wall_seconds'] for e in latest.values()),'peak_sampled_bytes':max(r['peak_sampled_bytes'] for r in processes),
        'source_anchors':source_anchors,'verifier_sha256':sha('scripts/verify_affine_feedback_unknown.py'),
        'core_verifier_sha256':sha('scripts/verify_affine_feedback.py'),
        'validation_seconds':time.perf_counter()-tick,'new_decryptions':[]}
    (ROOT/'results/phase26_unknown_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in summary.items() if k not in ('entries','sections','nulls')},flush=True)


if __name__=='__main__':main()
