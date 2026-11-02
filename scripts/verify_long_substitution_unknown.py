from collections import Counter
import json
import random
import time
from verify_terminated_benchmark import ROOT,load,sha,to_indices
from long_substitution_audit import SubstitutionVerifier
from verify_affine_feedback_unknown import CombinedVerifier
from liberprimus.boundaries import parse_layout


def main():
    tick=time.perf_counter();v=SubstitutionVerifier();anchors=CombinedVerifier.source_anchors(v)
    plan=load('experiments/long_substitution_unknown_plan.json');complete=load('checkpoints/phase30_unknown_complete.json')
    selection=load('experiments/long_substitution_selection.json')
    assert sha('experiments/long_substitution_selection.json')==complete['selection_sha256']
    assert sha(plan['control_validation'])==plan['control_validation_sha256'] and load(plan['control_validation'])['full_gate_passed']
    pages=[p for p in load('transcriptions/pages.json') if p['edition']=='LP2' and p['page']<=55]
    expected=[p['id'] for p in pages if p['rune_count']>=200]
    assert [p['page'] for p in plan['pages']]==expected and len(expected)==46
    assert plan['excluded_pages']==[{'reason':'non_rune_page' if not p['rune_count'] else 'below_preregistered_200_rune_scope','page':p} for p in pages if p['rune_count']<200]
    catalog={p['id']:p for p in pages};items={p['page']:p for p in plan['pages']}
    audit={p['page']:p['canonical']['segment_ends'] for p in load('results/E026-boundary-audit-314198a84563.json')['pages']}
    events=[json.loads(s) for s in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    by_output={e['output']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E084-')}
    assert len(by_output)==65 and set(by_output)==set(complete['outputs'])
    entries=[];observed=[];nulls=[]
    for path in complete['outputs']:
        assert time.perf_counter()-tick<900
        e=by_output[path];assert sha(path)==e['output_sha256']
        for p,h in e['input_dependencies'].items():assert sha(p)==h,p
        r=load(path);assert r['parameters']==plan and r['training']==v.training
        source=catalog[r['page']];item=items[r['page']];parsed=parse_layout(source['text_with_layout'])
        ends=parsed['segment_ends'];original=to_indices(source['runes'])
        assert parsed['runes']==source['runes'] and ends==item['segment_ends']==r['segment_ends']==audit[r['page']]
        assert item=={'page':source['id'],'number':source['page'],'runes':len(original),'segment_ends':ends,'source_refs':source['source_refs']}
        if r['mode']=='page':
            assert r['replicate']==0 and r['null_proposals'] is None and r['ciphertext_indices']==original
        else:
            assert r['mode']=='null' and r['page']==selection['page'] and r['replicate'] in range(19)
            rng=random.Random(plan['null_seed']+100*r['replicate']);eq=lambda p:sum(a==b for a,b in zip(p,p[1:]))
            for proposals in range(1,100001):
                mid=original[1:-1];rng.shuffle(mid);p=original[:1]+mid+original[-1:]
                if eq(p)==eq(original):break
            assert proposals==r['null_proposals'] and p==r['ciphertext_indices'] and Counter(p)==Counter(original)
        top=v.result(r['ciphertext_indices'],ends,r['result'])
        compact={'page':r['page'],'replicate':r['replicate'],'runes':len(original),'score':top['score'],'output':path}
        (observed if r['mode']=='page' else nulls).append(compact)
        entries.append({'id':e['experiment'],'output':path,'sha256':sha(path),'fingerprint':e['fingerprint']})
        print({'verified':e['experiment'],'seconds':time.perf_counter()-tick},flush=True)
    assert [r['page'] for r in observed]==expected and [r['replicate'] for r in nulls]==list(range(19))
    winner=max(observed,key=lambda r:r['score'])
    assert winner['page']==selection['page']==complete['page'] and winner['score']==selection['score']==complete['score']
    assert selection['source_outputs']=={r['output']:sha(r['output']) for r in observed}
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(1+exceed)/20
    assert complete['exceedances']==exceed and complete['raw_p']==p and complete['bonferroni46']==min(1,46*p)
    assert complete['pending_larger_calibration']==(exceed==0)
    result={'pages':observed,'nulls':nulls,'entries':entries,'selected_page':winner['page'],'score':winner['score'],
        'exceedances':exceed,'raw_p':p,'bonferroni46':min(1,46*p),'pending_larger_calibration':exceed==0,
        'source_anchors':anchors,'validation':dict(v.counts),'seconds':sum(e['wall_seconds'] for e in by_output.values()),
        'validation_seconds':time.perf_counter()-tick,'verifier_sha256':sha('scripts/verify_long_substitution_unknown.py'),
        'core_verifier_sha256':sha('scripts/long_substitution_audit.py'),'new_decryptions':[]}
    (ROOT/'results/phase30_unknown_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in result.items() if k not in ('pages','nulls','entries','source_anchors')})


if __name__=='__main__':main()
