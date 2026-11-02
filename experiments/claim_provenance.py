"""Bounded reproducible checks of publicly supplied evidence, not instructions."""
import hashlib
import re
import time
from attack_support import ROOT,load,digest
from registry import registered

FOLDER='sources/claim_repository_2026-10-20'
PLAN='experiments/claim_provenance_plan.json'
DIGESTS='results/E031-numeric-digest-comparison-6d699391d132.json'


def run():
    tick=time.perf_counter();manifest=load(FOLDER+'/manifest.json');files=load(FOLDER+'/files_manifest.json')
    for r in manifest['requests']+files['files']:
        if 'path' in r:assert digest(r['path'])==r['sha256']
    tree=load(FOLDER+'/tree-1.raw');assert manifest['tree_complete'] and len(tree)==manifest['tree_entries']
    for r in files['files']:
        data=(ROOT/r['path']).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert blob==r['git_blob_sha1']==next(t['id'] for t in tree if t['path']==r['source_path'])
    content=(ROOT/FOLDER/'index.raw').read_text(encoding='utf-8')
    preview={name:bytes.fromhex(re.search(pattern,content)[1]) for name,pattern in [
        ('first',r'First 32 bytes hex:\s*([0-9a-f]+)'),('last',r'Last 32 bytes hex:\s*([0-9a-f]+)')]}
    comparisons=[]
    for variant in load(DIGESTS)['variants']:
        data=bytes.fromhex(variant['byte_hex'])
        for name,offset in [('first',0),('last',224)]:
            observed=preview[name]
            comparisons.append({'source':variant['source'],'preview':name,'claimed_bytes':32,'actual_bytes':len(observed),
                'equal':observed==data[offset:offset+32],
                'differing_offsets':[offset+i for i,(a,b) in enumerate(zip(observed,data[offset:offset+32])) if a!=b],
                'deltas':[a-b for a,b in zip(observed,data[offset:offset+32]) if a!=b]})
    assert time.perf_counter()-tick<30
    return {'experiment':'E032-claim-provenance','parameters':load(PLAN),
        'pinned_commit':manifest['pinned_commit'],'tree_complete':manifest['tree_complete'],
        'tree_paths':[r['path'] for r in tree],
        'named_files_present':{name:any(r['path'].split('/')[-1]==name for r in tree)
                               for name in ('sexagesimal.bin','analyze_sexagesimal.zig')},
        'prior_html_byte_equal':(ROOT/FOLDER/'index.raw').read_bytes()==(ROOT/'sources/community_claim_2026-10-20/project.html').read_bytes(),
        'published_previews':{k:v.hex() for k,v in preview.items()},'preview_comparisons':comparisons,
        'historical_binary_provenance':'unverified','remote_code_executed':False,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


DEPS=['experiments/claim_provenance.py',PLAN,'experiments/attack_support.py',DIGESTS,
      'sources/community_claim_2026-10-20/project.html','scripts/acquire_claim_repository.py',
      'scripts/acquire_claim_files.py']+[FOLDER+'/'+p for p in
      ('manifest.json','files_manifest.json','head.raw','tree-1.raw','README.raw','index.raw')]

if __name__=='__main__':registered('E032-claim-provenance',load(PLAN),DEPS,run)
