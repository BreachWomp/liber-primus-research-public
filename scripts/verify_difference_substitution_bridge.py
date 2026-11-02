"""Literal cumulative-sum transport and source audit; no production difference code."""
import json
import random
import time
from verify_terminated_benchmark import Reference,ROOT,load,sha,to_indices


def main():
    tick=time.perf_counter();v=Reference();path=load('checkpoints/phase31_bridge_complete.json')['output'];row=load(path)
    events=[json.loads(s) for s in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    e=next(e for e in events if e['status']=='completed' and e['output']==path)
    assert sha(path)==e['output_sha256']
    for p,h in e['input_dependencies'].items():assert sha(p)==h,p
    validation=load('results/phase30_controls_validation.json');assert validation['full_gate_passed']
    assert row['parameters']==load('experiments/difference_substitution_plan.json') and len(row['rows'])==15
    by_output={r['output']:r for r in validation['entries']};done={e['output']:e for e in events if e['status']=='completed'}
    scores=0;identities=0;inverse_checks=0;controls=[]
    assert [r['source_output'] for r in row['rows']]==list(by_output)
    for r in row['rows']:
        assert time.perf_counter()-tick<180
        oldpath=r['source_output'];assert sha(oldpath)==r['source_sha256']==by_output[oldpath]['sha256']
        for p,h in done[oldpath]['input_dependencies'].items():assert sha(p)==h,p
        old=load(oldpath);s=old['source'];i=old['index'];block=i//3;chapter=('X','XI','XII')[i%3]
        source=[q for q in v.rows if q['chapter']==chapter and sum(map(len,q['words']))>=760][2+block]
        assert (s['chapter'],s['paragraph'])==(chapter,source['paragraph'])
        p,ends=v.source_window(s,len(source['words']));end=next(x for x in ends if x>=(200,300,500,729)[block])
        truth=p[:end];ends=[x for x in ends if x<=end]
        assert truth==s['plaintext_indices'] and ends==s['segment_ends']==r['segment_ends']
        perm=list(range(29));random.Random(3301083+i).shuffle(perm)
        assert perm==s['permutation_plain_to_cipher']
        delta=[perm[x] for x in truth];assert delta==s['ciphertext_indices']
        if old['kind']=='null':random.Random(3302083+old['replicate']).shuffle(delta)
        assert delta==old['ciphertext_indices']==r['difference_indices']
        assert (r['kind'],r['index'],r['replicate'])==(old['kind'],i,old['replicate'])
        c=[sum(delta[:j+1])%29 for j in range(len(delta))]
        assert c==r['ciphertext_indices']
        for iv in range(29):
            shifted=[(sum(delta[:j+1])+iv)%29 for j in range(len(delta))]
            back=[(x-y)%29 for x,y in zip(shifted,[iv]+shifted[:-1])]
            assert back==delta and len(back)==len(c);identities+=1
        for candidate in old['result']['restarts']:
            key=candidate['mapping_cipher_to_plain'];assert sorted(key)==list(range(29))
            plain=[key[(x-y)%29] for x,y in zip(c,[0]+c[:-1])]
            assert plain==to_indices(candidate['plaintext_runes'])
            assert abs(v.score(plain,ends)-candidate['score'])<1e-9;scores+=1
            again=[];previous=0
            for x in plain:
                step=next(k for k,val in enumerate(key) if val==x)
                previous=(previous+step)%29;again.append(previous)
            assert again==c;inverse_checks+=1
        top=old['result']['top'];assert top['score']==r['score']
        if r['kind']=='control':
            exact=to_indices(top['plaintext_runes'])==truth;assert r['exact']==exact
            controls.append({'index':i,'runes':len(truth),'exact':exact,'source_output':oldpath})
        else:assert r['exact'] is None
    gate=all(r['exact'] for r in controls);assert len(controls)==12 and gate==row['gate_passed']
    assert identities==row['iv_identity_checks'] and inverse_checks==row['reencryptions'] and row['new_optimizer_searches']==0
    result={'full_gate_passed':gate,'controls':controls,'entries':[{'id':e['experiment'],'fingerprint':e['fingerprint'],'output':path,'sha256':sha(path)}],
        'validation':{'independent_scores':scores,'all_iv_transport_checks':identities,'cumulative_reencryptions':inverse_checks,'raw_source_inputs':15},
        'seconds':e['wall_seconds'],'validation_seconds':time.perf_counter()-tick,
        'verifier_sha256':sha('scripts/verify_difference_substitution_bridge.py'),
        'limits':'Reused E083 capability, not new independent search recovery. Unknown attack IV0 only. Shared GP tokenizer, independent raw-source event counts and transport arithmetic.',
        'new_decryptions':[]}
    (ROOT/'results/phase31_bridge_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in result.items() if k not in ('controls','entries')})


if __name__=='__main__':main()
