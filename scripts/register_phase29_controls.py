from datetime import datetime,timezone
import json
from terminated_supervisor import ROOT,load,save
import hashlib

if __name__=='__main__':
    validation='results/phase29_benchmark_validation.json';assert load(validation)['gate_passed']
    path='experiments/terminated_controls_plan.json';assert not (ROOT/path).exists()
    save(path,{'registered_at':datetime.now(timezone.utc).isoformat(),'experiment':'E081','hypothesis':'H031',
        'benchmark_validation':validation,'benchmark_validation_sha256':hashlib.sha256((ROOT/validation).read_bytes()).hexdigest(),
        'controls':9,'regressions':load('experiments/terminated_substitution_plan.json')['regressions'],
        'external':'Indices3..5:chaptersX,XI,XII, first paragraph with >=350runes, take whole-word prefix until >=66runes. Indices6..8: same chapters, second eligible paragraph, whole-word prefix until >=300runes. All GP tokenization unchanged. Previously inspected source, excluded from fitting.',
        'permutation':'Random3301081+index independently shuffles0..28 as plaintext-to-cipher mapping. Search sees ciphertext and endpoints only. Exact recovery required only on observed symbols; absent symbols cannot be identified.',
        'search':'E036 unchanged at most24 pattern/frequency/random starts,40 all406-swap character sweeps then40 all406-swap new word-score sweeps; warmup character model still excludesX/XI/XII. Seeds3303081+100*index. No LP words injected. No adaptive restarts.',
        'null':'Three diagnostic full-search exact-count shuffles of control2, seed3302081+replicate, same endpoints and optimizer seed as control. No p-value or doublet conditioning; capability diagnostic only.',
        'gate':'All9 top-one plaintexts exact, independent scores/mapping/source/local-optimum validation. Every control and all3 diagnostic nulls run even if a control fails. No unknown scan if gate fails.',
        'bounds':load('experiments/terminated_substitution_plan.json')['bounds'],
        'followup':'Only after independent full gate, separately preregister unknown pages E082 with full optimizer matched nulls and selection correction. No tuning on unknown output.'})
    print({'registered':'E081','controls':9,'nulls':3})
