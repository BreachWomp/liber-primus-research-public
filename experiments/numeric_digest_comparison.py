"""Compare exactly five already-preserved numeric readings to published digests."""
import hashlib
import time
from attack_support import load
from registry import registered

PLAN='experiments/numeric_digest_plan.json'
AUDIT='results/E022-numeric-source-audit-7f284cff4638.json'
GLYPH='results/E023-glyph-audit-8315f5c684bb.json'


def run():
    tick=time.perf_counter();plan=load(PLAN);audit=load(AUDIT);glyph=load(GLYPH)
    alphabet=audit['alphabet'];variants={};coordinates=[]
    for page in audit['pages']:
        for i,row in enumerate(page['published_decimal']):
            for j,_ in enumerate(row):coordinates.append([page['page_id'],i+1,j+1])
    for name in ('relikd_canonical','iddqd','scream314'):
        values=[]
        for page in audit['pages']:
            calc=[[60*alphabet.index(t[0])+alphabet.index(t[1]) for t in row] for row in page['tokens_by_source'][name]]
            assert calc==page['values_by_source'][name]
            values.extend(v for row in calc for v in row)
        variants[name]=bytes(values)
    variants['scream314_published_decimal']=bytes(v for page in audit['pages'] for row in page['published_decimal'] for v in row)
    variants['image_overlay_E023']=bytes.fromhex(glyph['byte_hex'])
    baseline=variants['image_overlay_E023'];assert hashlib.sha256(baseline).hexdigest()==glyph['byte_sha256']
    rows=[]
    for name,data in variants.items():
        assert len(data)==256
        digest=hashlib.sha256(data).hexdigest()
        rows.append({'source':name,'byte_hex':data.hex(),'sha256':digest,'matches_targets':[t for t in plan['targets'] if t==digest],
                     'differences_from_image_overlay':[{'offset':i,'page':coordinates[i][0],'row':coordinates[i][1],
                        'column':coordinates[i][2],'baseline':baseline[i],'value':v,'delta':v-baseline[i]}
                        for i,v in enumerate(data) if v!=baseline[i]]})
    assert time.perf_counter()-tick<plan['seconds']
    return {'experiment':'E031-numeric-digest-comparison','parameters':plan,'variants':rows,
            'unmatched_targets':[t for t in plan['targets'] if not any(t==r['sha256'] for r in rows)],
            'wall_seconds':time.perf_counter()-tick,'canonical_changed':False,'new_decryptions':[]}


if __name__=='__main__':registered('E031-numeric-digest-comparison',load(PLAN),[
    'experiments/numeric_digest_comparison.py',PLAN,'experiments/attack_support.py',AUDIT,GLYPH,
    'sources/community_claim_2026-10-20/project.html','sources/community_claim_2026-10-20/manifest.json'],run)
