"""Independent E059 source/null replay, full selection audit and score checks."""
from collections import Counter
import json
from pathlib import Path
import random
import time
from verify_constrained_fragments import ConstraintVerifier,load,sha,to_indices
ROOT=Path(__file__).resolve().parents[1]


def verify():
    tick=time.perf_counter();plan=load('experiments/constrained_unknown_plan.json')
    complete=load('checkpoints/phase21_unknown_complete.json');assert len(complete['outputs'])==28
    selection=load('experiments/constrained_selection.json')
    assert sha('experiments/constrained_selection.json')==complete['selection_sha256']
    assert load(plan['control_validation'])['full_gate_passed']
    catalog={p['id']:p for p in load('transcriptions/pages.json')}
    groups={g['id']:g for g in load('experiments/section_plan.json')['sections']}
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    latest={e['output']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E059-')}
    assert set(latest)==set(complete['outputs']);v=ConstraintVerifier();sections=[];nulls=[];entries=[];coverage=set();empty=set()
    doublets=lambda a:sum(x==y for x,y in zip(a,a[1:]))
    for path in complete['outputs']:
        assert time.perf_counter()-tick<600,'Validation budget600s'
        event=latest[path];assert event['wall_seconds']<180 and sha(path)==event['output_sha256']
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path);group=groups[row['section']];assert row['group']==group
        assert row['training']['training_source_ranges']==v.ranges
        assert row['training']['source_sha256']==sha('data/raw/gutenberg/pg2944.txt')
        source=[];spans=[]
        for page in group['page_ids']:
            piece=to_indices(catalog[page]['runes']);start=len(source);source+=piece
            spans.append({'page_id':page,'start':start,'end':len(source),'runes':len(piece),
                          'source_refs':catalog[page]['source_refs'],'zero_rune_page':not bool(piece)})
        assert spans==row['page_spans'] and row['section'] in plan['section_ids']
        args=row['parameters']
        if args['mode']=='section':
            assert source==row['ciphertext_indices'] and row['page_proposals'] is None
            assert args['replicate']==0
            coverage.update(s['page_id'] for s in spans if s['runes'])
            empty.update(s['page_id'] for s in spans if not s['runes'])
        else:
            assert row['section']==selection['selected_section'] and 0<=args['replicate']<19
            out=[];records=[];seed=plan['null_seed']+100*args['replicate']
            for j,span in enumerate(spans):
                piece=source[span['start']:span['end']]
                if len(piece)<=2:sample=piece[:];proposals=0
                else:
                    rng=random.Random(seed+j)
                    for proposals in range(1,100001):
                        middle=piece[1:-1];rng.shuffle(middle);sample=piece[:1]+middle+piece[-1:]
                        if doublets(sample)==doublets(piece):break
                    else:raise AssertionError('Null rejection cap')
                assert Counter(sample)==Counter(piece)
                out+=sample;records.append({'page_id':span['page_id'],'seed':seed+j,'proposals':proposals})
            assert out==row['ciphertext_indices'] and records==row['page_proposals']
            assert Counter(out)==Counter(source) and doublets(out)==doublets(source)
        v.result(row['ciphertext_indices'],row['result'],row['page_spans'])
        assert row['score']==row['result']['top'][0]['score'] and row['new_decryptions']==[]
        compact={'section':row['section'],'score':row['score'],'runes':len(source),'output':path,
                 'key_length':len(row['result']['top'][0]['key']),'replicate':args['replicate']}
        (sections if args['mode']=='section' else nulls).append(compact)
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        print({'verified':event['experiment'],**v.counts},flush=True)
    assert [r['section'] for r in sections]==plan['section_ids']
    assert [r['replicate'] for r in nulls]==list(range(19))
    winner=max(sections,key=lambda r:r['score']);assert winner['section']==selection['selected_section']==complete['selected_section']
    assert winner['score']==selection['observed_score']==complete['observed_score']
    assert selection['source_outputs']=={r['output']:sha(r['output']) for r in sections}
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(1+exceed)/20
    assert complete['exceedances']==exceed and complete['raw_p']==p and complete['bonferroni9']==min(1,9*p)
    assert complete['pending_larger_calibration']==(exceed==0)
    processes=load('results/phase21_unknown_processes.json')
    assert all(r['exit_code']==0 and r['reason'] is None and r['peak_sampled_bytes']<=768*1024**2 for r in processes)
    assert complete['seconds']+complete['prior_seconds']<plan['family_seconds']
    summary={'experiment':'E059','sections':sections,'nulls':nulls,'selected_section':winner['section'],
             'observed_score':winner['score'],'exceedances':exceed,'raw_p':p,'bonferroni9':min(1,9*p),
             'pending_larger_calibration':exceed==0,'unique_unknown_rune_pages':len(coverage),'empty_pages_preserved':sorted(empty),
             'seconds':sum(e['wall_seconds'] for e in latest.values()),'successful_tasks':28,
             'peak_sampled_bytes':max(r['peak_sampled_bytes'] for r in processes),
             'validation':dict(v.counts),'validation_seconds':time.perf_counter()-tick,'entries':entries,'new_decryptions':[]}
    (ROOT/'results/phase21_unknown_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:x for k,x in summary.items() if k not in ('entries','sections','nulls')}),flush=True)
    return summary


if __name__=='__main__':verify()
