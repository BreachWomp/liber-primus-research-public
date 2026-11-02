"""Compare lexical boundaries while retaining every source layout byte."""
import time
from attack_support import load,ROOT,digest,to_indices
from registry import registered
from liberprimus.boundaries import parse_layout,segments
from liberprimus.alphabet import transliterate

MASTER='data/raw/iddqd/liber-primus__transcription--master/liber-primus__transcription--master.txt'

def run():
    tick=time.perf_counter();pages=load('transcriptions/pages.json')
    master=(ROOT/MASTER).read_text(encoding='utf-8').split('\n\n',1)[1].split('%')
    rows=[]
    for p in pages:
        canonical=parse_layout(p['text_with_layout']);assert canonical['runes']==p['runes'],p['id']
        index=(15+p['page']) if p['edition']=='LP2' else (0 if p['page']==1 else p['page']-2 if p['page']>=3 else None)
        comparison=parse_layout(master[index]) if index is not None else None
        agree=comparison is not None and comparison['runes']==p['runes'] and comparison['segment_ends']==canonical['segment_ends']
        rows.append({'page':p['id'],'source_refs':p['source_refs'],'canonical':canonical,
            'iddqd_master_index':index,'iddqd':comparison,'boundary_and_rune_agreement':agree,
            'internal_canonical_only':sorted(set(canonical['segment_ends'][:-1])-set(comparison['segment_ends'][:-1])) if comparison else [],
            'internal_iddqd_only':sorted(set(comparison['segment_ends'][:-1])-set(canonical['segment_ends'][:-1])) if comparison else [],
            'eligible_unknown':bool(agree and p['edition']=='LP2' and p['page']<=55 and p['runes'])})
    byid={p['id']:p for p in pages};controls=[]
    for fixture in load('known_solutions/fixtures.json'):
        if not fixture['canonical_pages_match']:continue
        layout=parse_layout('\n'.join(byid[ident]['text_with_layout'] for ident in fixture['page_ids']))
        assert layout['runes']==fixture['ciphertext_runes']
        plain=to_indices(fixture['plaintext_runes'])
        controls.append({'fixture':fixture['id'],'page_ids':fixture['page_ids'],'segment_ends':layout['segment_ends'],
            'rendered_plaintext_segments':' '.join(transliterate(part) for part in segments(plain,layout['segment_ends']))})
    assert time.perf_counter()-tick<30
    return {'experiment':'E026-boundary-audit','status':'completed','pages':rows,'controls':controls,
        'eligible_unknown_pages':[r['page'] for r in rows if r['eligible_unknown']],
        'conflicting_LP2_pages':[r['page'] for r in rows if r['page'].startswith('LP2') and not r['boundary_and_rune_agreement']],
        'master_sha256':digest(MASTER),'canonical_sha256':digest('transcriptions/pages.json'),
        'limits':['Source agreement is not proof of independent provenance or correct plaintext word boundaries.',
                  'No all-page image audit. Apostrophes split lexical segments by explicit modeling convention.',
                  'Physical lines/pages do not create inferred cuts; non-rune content is retained separately.'],
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}

if __name__=='__main__':
    registered('E026-boundary-audit',{'seconds':30,'seed':None},['experiments/boundary_audit.py',
        'experiments/boundary_audit_plan.json','src/liberprimus/boundaries.py','src/liberprimus/alphabet.py',
        'experiments/attack_support.py','transcriptions/pages.json','known_solutions/fixtures.json',MASTER,'sources/manifest.json'],run)
