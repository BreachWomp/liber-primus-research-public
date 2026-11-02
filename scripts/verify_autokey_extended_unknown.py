"""Independent E063 sources, endpoint nulls, full scoring and selection audit."""
import json
import random
import time
from verify_autokey_extended import ROOT,load,sha,Verifier,to_indices


def main():
    tick=time.perf_counter();v=Verifier();plan=load('experiments/autokey_extended_unknown_plan.json')
    complete=load('checkpoints/phase22_unknown_complete.json');selection=load('experiments/autokey_extended_selection.json')
    assert sha('experiments/autokey_extended_selection.json')==complete['selection_sha256']
    assert load(plan['control_validation'])['full_gate_passed']
    catalog={p['id']:p for p in load('transcriptions/pages.json')}
    eligible=[p['id'] for p in catalog.values() if p['edition']=='LP2' and p['page']<=55 and 200<=len(p['runes'])<=729]
    assert eligible==plan['page_ids'] and len(eligible)==46
    excluded=[p for p in catalog.values() if p['edition']=='LP2' and p['page']<=55 and p['id'] not in eligible]
    assert [(p['id'],len(p['runes'])) for p in excluded]==[(r['page'],r['runes']) for r in plan['excluded_pages']]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    latest={e['output']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E063-')}
    assert set(latest)==set(complete['outputs']) and len(latest)==65
    entries=[];pages=[];nulls=[]
    for path in complete['outputs']:
        assert time.perf_counter()-tick<900
        event=latest[path];assert sha(path)==event['output_sha256'] and event['wall_seconds']<180
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);assert row['parameters']==plan and row['training']==v.training
        page=catalog[row['page']];assert row['source_refs']==page['source_refs'] and page['id'] in eligible
        original=to_indices(page['runes'])
        if row['mode']=='page':
            assert row['replicate']==0 and row['proposals']==0 and row['ciphertext_indices']==original
        else:
            assert row['mode']=='null' and row['page']==selection['page'] and 0<=row['replicate']<19
            rng=random.Random(plan['null_seed']+row['replicate']);doublets=lambda a:sum(x==y for x,y in zip(a,a[1:]))
            for proposals in range(1,100001):
                middle=original[1:-1];rng.shuffle(middle);sample=original[:1]+middle+original[-1:]
                if doublets(sample)==doublets(original):break
            else:raise AssertionError('Rejection cap')
            assert sample==row['ciphertext_indices'] and proposals==row['proposals']
        v.result(row['ciphertext_indices'],row['result'])
        top=row['result']['top'][0]
        compact={'page':row['page'],'replicate':row['replicate'],'runes':len(original),'score':top['score'],
            'key_length':len(top['recipe']['key_indices']),'output':path}
        (pages if row['mode']=='page' else nulls).append(compact)
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        assert row['new_decryptions']==[]
        print({'verified':event['experiment'],**v.counts},flush=True)
    assert [r['page'] for r in pages]==eligible and [r['replicate'] for r in nulls]==list(range(19))
    winner=max(pages,key=lambda r:r['score'])
    assert selection['page']==winner['page']==complete['page'] and selection['score']==winner['score']==complete['score']
    assert selection['source_outputs']=={r['output']:sha(r['output']) for r in pages}
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(1+exceed)/20
    assert complete['exceedances']==exceed and complete['raw_p']==p and complete['bonferroni46']==min(1,46*p)
    assert complete['pending_larger_calibration']==(exceed==0)
    processes=load('results/phase22_unknown_processes.json')
    assert len(processes)==65 and all(r['exit_code']==0 and r['reason'] is None and r['peak_sampled_bytes']<=768*1024**2 for r in processes)
    assert complete['seconds']+complete['prior_seconds']<plan['family_seconds']
    summary={'pages':pages,'nulls':nulls,'selected_page':winner['page'],'score':winner['score'],
        'exceedances':exceed,'raw_p':p,'bonferroni46':min(1,46*p),'pending_larger_calibration':exceed==0,
        'excluded_pages':plan['excluded_pages'],'entries':entries,'validation':dict(v.counts),
        'seconds':sum(e['wall_seconds'] for e in latest.values()),'peak_sampled_bytes':max(r['peak_sampled_bytes'] for r in processes),
        'validation_seconds':time.perf_counter()-tick,'new_decryptions':[]}
    (ROOT/'results/phase22_unknown_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in summary.items() if k not in ('entries','pages','nulls','excluded_pages')},flush=True)


if __name__=='__main__':main()
