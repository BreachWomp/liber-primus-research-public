"""Validate source-linked glyph observations and materialize an explicit overlay."""
import hashlib
import time
from attack_support import ROOT, load, digest
from registry import registered
from liberprimus.numeric import apply_overlay, decode_pair, encode_pair

E022 = 'results/E022-numeric-source-audit-7f284cff4638.json'

def run():
    tick = time.perf_counter()
    prior = load(E022); manifest = load('sources/glyph_crop_manifest.json')
    observations = load('sources/glyph_observations.json')
    crops = {(c['page_id'],c['row_1based'],c['column_1based']): c for c in manifest['crops']}
    for c in crops.values():
        assert digest(c['image_path']) == c['image_sha256']
        assert digest(c['crop_path']) == c['crop_sha256']
        assert len(c['ink_measurements']) == 3
    assert digest(manifest['contact_sheet']['path']) == manifest['contact_sheet']['sha256']
    old = {(c['page_id'],c['row_1based'],c['column_1based']): c for c in prior['source_disagreements']}
    assert len(observations['observations']) == len(old) == 5
    for item in observations['observations']:
        key = (item['page_id'],item['row_1based'],item['column_1based'])
        assert set(item['historical_alternatives']) == set(old[key]['tokens'].values())
        assert key in crops
        assert all(tuple(ref) in crops for ref in item['comparison_cells'])
    grids = apply_overlay(prior['pages'], observations['observations'])
    cells = []
    for page, rows in grids.items():
        for r,row in enumerate(rows,1):
            for c,token in enumerate(row,1):
                value = decode_pair(token)
                assert 0 <= value < 256 and encode_pair(value) == token
                cells.append({'page_id':page,'row_1based':r,'column_1based':c,'token':token,'value':value})
    payload = bytes(c['value'] for c in cells)
    assert len(payload) == 256
    assert all(grids[p['page_id']] == p['tokens_by_source']['iddqd'] for p in prior['pages'])
    assert time.perf_counter()-tick < 30
    return {'experiment':'E023-glyph-audit','status':'completed','image_supported_cells':5,
        'unresolved_among_original_five':0,'inspected_crops':len(crops),
        'observations':observations,'overlay_grids':grids,'cells':cells,
        'byte_order':'LP2-49, LP2-50, LP2-51; table rows top to bottom, cells left to right',
        'byte_hex':payload.hex(),'byte_sha256':hashlib.sha256(payload).hexdigest(),
        'canonical_changed':False,'matches_prior_iddqd_tokens':True,
        'inference':'Source transcription refinement and prior-art Base60 replication; no decryption.',
        'null_model':'Not applicable: deterministic source/measurement audit.',
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}

if __name__ == '__main__':
    manifest = load('sources/glyph_crop_manifest.json')
    deps = ['experiments/glyph_audit.py','experiments/glyph_audit_plan.json',E022,
            'experiments/attack_support.py','src/liberprimus/numeric.py',
            'sources/glyph_observations.json','sources/glyph_crop_manifest.json',
            'sources/layout_audit.json','scripts/prepare_glyph_crops.py','transcriptions/pages.json']
    deps += [p for c in manifest['crops'] for p in (c['image_path'], c['crop_path'])]
    deps += [manifest['contact_sheet']['path']]
    registered('E023-glyph-audit', {'max_seconds':30,'seed':None,'thresholds':[32,128,224]}, deps, run)
