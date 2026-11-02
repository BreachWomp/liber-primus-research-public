"""Source-anchored independent exhaustive-prefix and matched-null audit for E076."""
import json
import time
from verify_delay_three import DelayThreeVerifier,ROOT,load,sha


def main():
    tick=time.perf_counter();v=DelayThreeVerifier();anchors=v.source_anchors()
    plan=load('experiments/delay_three_unknown_plan.json');complete=load('checkpoints/phase27_unknown_complete.json')
    selection=load('experiments/delay_three_selection.json')
    assert sha('experiments/delay_three_selection.json')==complete['selection_sha256']
    assert sha(plan['control_validation'])==plan['control_validation_sha256'] and load(plan['control_validation'])['full_gate_passed']
    catalog={p['id']:p for p in load('transcriptions/pages.json')}
    assert plan['preserved_non_rune_pages']==[catalog['LP2-50']]
    groups={g['id']:g for g in plan['groups']};assert len(groups)==55
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    by_output={e['output']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E076-')}
    assert len(by_output)==74 and set(by_output)==set(complete['outputs'])
    entries=[];pages=[];nulls=[]
    for path in complete['outputs']:
        assert time.perf_counter()-tick<900
        e=by_output[path];assert sha(path)==e['output_sha256']
        for dep,digest in e['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);assert row['parameters']==plan and row['training']==v.training
        group=groups[row['page']];assert row['group']==group
        original,spans=v.spans(group);assert row['page_spans']==spans
        if row['mode']=='page':
            assert row['replicate']==0 and row['page_proposals'] is None and row['ciphertext_indices']==original
        else:
            assert row['mode']=='null' and row['page']==selection['page'] and 0<=row['replicate']<19
            sample,proposals=v.null(original,spans,plan['null_seed']+100*row['replicate'])
            assert sample==row['ciphertext_indices'] and proposals==row['page_proposals']
        v.result(row['ciphertext_indices'],row['result'])
        top=row['result']['top'][0];recipe=top['recipe']
        compact={'page':row['page'],'replicate':row['replicate'],'runes':len(original),'score':top['score'],
            'a':recipe['cipher_sign'],'b':recipe['feedback_sign'],'c':recipe['constant'],'output':path}
        (pages if row['mode']=='page' else nulls).append(compact)
        entries.append({'id':e['experiment'],'fingerprint':e['fingerprint'],'output':path,'sha256':e['output_sha256']})
        print({'verified':e['experiment'],'seconds':time.perf_counter()-tick},flush=True)
    assert [r['page'] for r in pages]==plan['section_ids'] and [r['replicate'] for r in nulls]==list(range(19))
    winner=max(pages,key=lambda r:r['score'])
    assert selection['page']==winner['page']==complete['page'] and selection['score']==winner['score']==complete['score']
    assert selection['source_outputs']=={r['output']:sha(r['output']) for r in pages}
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(1+exceed)/20
    assert complete['exceedances']==exceed and complete['raw_p']==p and complete['bonferroni55']==min(1,55*p)
    assert complete['pending_larger_calibration']==(exceed==0)
    result={'pages':pages,'nulls':nulls,'selected_page':winner['page'],'score':winner['score'],
        'exceedances':exceed,'raw_p':p,'bonferroni55':min(1,55*p),'pending_larger_calibration':exceed==0,
        'entries':entries,'source_anchors':anchors,'validation':dict(v.counts),
        'seconds':sum(e['wall_seconds'] for e in by_output.values()),'validation_seconds':time.perf_counter()-tick,
        'verifier_sha256':sha('scripts/verify_delay_three_unknown.py'),'core_verifier_sha256':sha('scripts/verify_delay_three.py'),
        'new_decryptions':[]}
    (ROOT/'results/phase27_unknown_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in result.items() if k not in ('pages','nulls','entries','source_anchors')})


if __name__=='__main__':main()
