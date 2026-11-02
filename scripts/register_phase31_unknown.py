from datetime import datetime,timezone
import hashlib
from difference_substitution_supervisor import ROOT,load,save
from liberprimus.boundaries import parse_layout

if __name__=='__main__':
    validation='results/phase31_bridge_validation.json';v=load(validation)
    assert v['full_gate_passed'] and len(v['controls'])==12
    path='experiments/difference_substitution_unknown_plan.json';assert not (ROOT/path).exists()
    allpages=[p for p in load('transcriptions/pages.json') if p['edition']=='LP2' and p['page']<=55]
    pages=[];excluded=[]
    for p in allpages:
        if p['rune_count']<200:
            excluded.append({'reason':'non_rune_page' if not p['rune_count'] else 'below_preregistered_200_rune_scope','page':p});continue
        parsed=parse_layout(p['text_with_layout']);assert parsed['runes']==p['runes']
        ends=parsed['segment_ends'];assert max(b-a for a,b in zip([0]+ends[:-1],ends))<=32
        pages.append({'page':p['id'],'number':p['page'],'runes':p['rune_count'],'segment_ends':ends,'source_refs':p['source_refs']})
    assert len(pages)==46 and len(excluded)==10
    save(path,{'registered_at':datetime.now(timezone.utc).isoformat(),'experiment':'E086','hypothesis':'H052',
        'control_validation':validation,'control_validation_sha256':hashlib.sha256((ROOT/validation).read_bytes()).hexdigest(),
        'pages':pages,'excluded_pages':excluded,
        'search':'FixedIV0:D0=C0,Di=(Ci-Cprev)mod29; all runes retained and lexical endpoints unchanged. Frozen E083/E081 substitution solver on D and BOS/EOS word objective, no new starts/parameters. Per page search seed3303086+100*originalLP2number, reused identically in all of that page\'s nulls. No runes omitted; original lexical endpoints fixed. Full per-restart outputs retained.',
        'selection':'Maximum mean word score over46pages, stable page-order ties; freeze winner and all46 output hashes before any null draws.',
        'null_seed':3302086,'replicates':19,
        'null':'Original C-space selected-page independent interior shuffles preserving first/last rune, exact counts, adjacent-equality count, fixed original segment ends. Random(null_seed+100*replicate), max100000 proposals; After shuffling C, compute D withIV0 and run full identical optimizer; D counts are not fixed.',
        'inference':'Plus-one p=(1+exceedances)/20, Bonferroni46. Minimum corrected p is1, coarse screening only. Zero exceedances requires separately preregistered larger calibration, not pooled adaptive sampling.',
        'bounds':load('experiments/difference_substitution_plan.json')['bounds'],
        'limits':'E085 transports12 prior controls exactly without new optimizer searches. Unknown IV is fixed0, other IVs untested; capability does not prove the cipher. Source boundaries/page edges may not be plaintext word boundaries. Finite29-symbol bijection search, no exhaustive29! claim; no scope extrapolation to short pages.'})
    print({'registered':'E086','pages':len(pages),'preserved_exclusions':len(excluded)})
