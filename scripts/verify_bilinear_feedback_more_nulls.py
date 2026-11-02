"""Independent audit of all99 fresh E070 null searches; no pooled inference."""
import json
import time
from verify_bilinear_feedback_unknown import ROOT,load,sha,CombinedVerifier


def main():
    tick=time.perf_counter();v=CombinedVerifier();plan=load('experiments/bilinear_feedback_more_null_plan.json')
    base=load('experiments/bilinear_feedback_unknown_plan.json');complete=load('checkpoints/phase25_more_nulls_complete.json')
    assert sha(plan['original_validation'])==plan['original_validation_sha256']
    old=load(plan['original_validation']);assert old['exceedances']==0 and old['pending_larger_calibration']
    assert sha('experiments/bilinear_feedback_selection.json')==plan['selection_sha256']==complete['selection_sha256']
    selection=load('experiments/bilinear_feedback_selection.json');assert selection['section']==plan['section'] and selection['score']==plan['observed_score']
    group=next(g for g in base['groups'] if g['id']==plan['section']);original,spans=v.spans(group)
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    latest={e['output']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E070-')}
    assert set(latest)==set(complete['outputs']) and len(latest)==99
    entries=[];nulls=[]
    for index,path in zip(plan['replicates'],complete['outputs']):
        assert time.perf_counter()-tick<1200
        event=latest[path];assert sha(path)==event['output_sha256'] and event['wall_seconds']<180
        for dep,digest in event['input_dependencies'].items():assert sha(dep)==digest,dep
        row=load(path)
        assert row['experiment']=='E070' and row['mode']=='null' and row['replicate']==index
        assert row['parameters']==base and row['extension_plan']==plan and row['training']==v.training
        assert row['group']==group and row['page_spans']==spans and row['section']==plan['section']
        sample,proposals=v.null(original,spans,base['null_seed']+100*index)
        assert row['ciphertext_indices']==sample and row['page_proposals']==proposals
        v.coefficients.clear();v.windows.clear();v.result(sample,row['result']);v.continuous(sample,spans,row['result'])
        top=row['result']['top'][0]
        nulls.append({'replicate':index,'score':top['score'],'key_length':len(top['recipe']['key_indices']),'output':path})
        entries.append({'id':event['experiment'],'fingerprint':event['fingerprint'],'output':path,'sha256':event['output_sha256']})
        assert row['new_decryptions']==[]
        print({'verified':event['experiment'],'seconds':time.perf_counter()-tick},flush=True)
    assert [r['replicate'] for r in nulls]==list(range(19,118))
    exceed=sum(r['score']>=selection['score'] for r in nulls);p=(1+exceed)/100
    assert complete['exceedances']==exceed and complete['raw_p']==p and complete['bonferroni56']==min(1,56*p)
    assert complete['pending_larger_calibration']==(exceed==0)
    processes=load('results/phase25_more_nulls_processes.json')
    assert len(processes)==99 and all(r['exit_code']==0 and r['reason'] is None and r['peak_sampled_bytes']<=768*1024**2 for r in processes)
    assert complete['seconds']+complete['prior_seconds']<plan['family_seconds']
    summary={'selected_section':selection['section'],'score':selection['score'],'fresh_null_count':99,
        'original_screen_count':19,'original_screen_exceedances':0,'exceedances':exceed,'raw_p':p,'bonferroni56':min(1,56*p),
        'inference':'Fresh99 only; original19 not pooled into an adaptive pvalue.',
        'pending_larger_calibration':exceed==0,'nulls':nulls,'entries':entries,'validation':dict(v.counts),
        'seconds':sum(e['wall_seconds'] for e in latest.values()),'peak_sampled_bytes':max(r['peak_sampled_bytes'] for r in processes),
        'validation_seconds':time.perf_counter()-tick,'verifier_sha256':sha('scripts/verify_bilinear_feedback_more_nulls.py'),'new_decryptions':[]}
    (ROOT/'results/phase25_more_nulls_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in summary.items() if k not in ('entries','nulls')},flush=True)


if __name__=='__main__':main()
