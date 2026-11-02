"""Preregister E079 after independent controls; all55 individual rune pages."""
from datetime import datetime,timezone
import json
from attack_support import ROOT,load,digest

if __name__=='__main__':
    validation=load('results/phase28_controls_validation.json')
    assert validation['full_gate_passed'] and len(validation['controls'])==16
    path=ROOT/'experiments/delay_two_unknown_plan.json';assert not path.exists()
    pages=[p for p in load('transcriptions/pages.json') if p['edition']=='LP2' and p['page']<=55]
    groups=[{'id':p['id'],'page_ids':[p['id']],'source_refs':p['source_refs']} for p in pages if p['rune_count']]
    assert len(groups)==55
    plan={'registered_at':datetime.now(timezone.utc).isoformat(),'experiment':'E079','hypothesis':'H050',
        'groups':groups,'section_ids':[g['id'] for g in groups],
        'preserved_non_rune_pages':[p for p in pages if not p['rune_count']],
        'solver':'Frozen E077/E078:delay2,a,b1..28,c0..28,top128 unigram families, all841 prefixes exact per retained family. No omissions or hidden resets.',
        'control_validation':'results/phase28_controls_validation.json','control_validation_sha256':digest('results/phase28_controls_validation.json'),
        'selection':'Highest mean fourgram score among55 inputs; stable page order for ties. Freeze all55 output hashes and winner before nulls.',
        'null_seed':3302079,'replicates':19,'null':'19 independent selected-page interior shuffles preserving endpoints,counts,doublets; cap100000 proposals. Entire screen and exhaustive retained-family prefix search repeated.',
        'inference':'Plus-one p=(1+exceedances)/20, Bonferroni55. Minimum corrected p is1; coarse screening, no significance claim. Zero exceedances triggers separately preregistered larger calibration.',
        'bounds':load('experiments/delay_two_plan.json')['bounds'],
        'limits':'Only128 of22736 coefficient/constant families retained. Exactness applies only to their prefix space. English-prose model, no interrupted updates. No community solution claims.'}
    path.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print({'registered':'E079','pages':55,'non_rune_preserved':'LP2-50'})
