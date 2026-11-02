"""E085 exact transport of previously validated E083 capability, no new search."""
import time
from attack_support import load,to_indices,digest
from long_substitution_controls import DEPS as OLD_DEPS
from liberprimus.difference_substitution import differences,integrate,decode,encode
from registry import registered
PLAN='experiments/difference_substitution_plan.json'


def run():
    tick=time.perf_counter();validation=load('results/phase30_controls_validation.json');assert validation['full_gate_passed']
    rows=[];reencryptions=0;iv_checks=0
    for entry in validation['entries']:
        assert digest(entry['output'])==entry['sha256'];old=load(entry['output']);delta=old['ciphertext_indices']
        c=integrate(delta,0);assert differences(c,0)==delta and len(c)==len(delta)
        for iv in range(29):
            test=integrate(delta,iv);assert differences(test,iv)==delta
            assert test==[(x+iv)%29 for x in c];iv_checks+=1
        for r in old['result']['restarts']:
            key=r['mapping_cipher_to_plain'];p=to_indices(r['plaintext_runes'])
            assert decode(c,key,0)==p and encode(p,key,0)==c;reencryptions+=1
        exact=None if old['kind']=='null' else decode(c,old['result']['top']['mapping_cipher_to_plain'],0)==old['source']['plaintext_indices']
        rows.append({'source_output':entry['output'],'source_sha256':entry['sha256'],'kind':old['kind'],'index':old['index'],
            'replicate':old['replicate'],'ciphertext_indices':c,'difference_indices':delta,
            'segment_ends':old['source']['segment_ends'],'exact':exact,'score':old['result']['top']['score']})
    assert time.perf_counter()-tick<180
    return {'experiment':'E085','parameters':load(PLAN),'rows':rows,'gate_passed':all(r['exact'] for r in rows if r['kind']=='control'),
        'reused_searches':15,'new_optimizer_searches':0,'iv_identity_checks':iv_checks,'reencryptions':reencryptions,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


DEPS=OLD_DEPS+[PLAN,'experiments/difference_substitution_bridge.py','src/liberprimus/difference_substitution.py',
    'results/phase30_controls_validation.json','scripts/difference_substitution_supervisor.py','scripts/run_difference_substitution_bridge.py']
if __name__=='__main__':
    prior=[r['output'] for r in load('results/phase30_controls_validation.json')['entries']]
    registered('E085-reversible-bridge',load(PLAN),DEPS+prior,run)
