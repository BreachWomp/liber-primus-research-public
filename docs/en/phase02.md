# Phase 2: Selective interruptions, dictionary keys, and autokey

**No new decryption confirmed.** Historical report date: 2026-10-19T09:21:02.072379+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

All 55 unknown LP2 rune pages were tested. LP2-50 remains in the corpus with its
numeric layout but is outside these rune-only attacks.

| Experiment | Declared search or control | Outcome |
|---|---|---|
| E006 | Six separate LP1 training/test sections; 1,200 mutations; known keys with all F subsets | Truth wins 1,105 comparisons; one interruption control exact, two inexact |
| E007 | 381 primitive word-key cycles, both word orders, all phases, four signs | 83,820 key/sign tasks and 472,340 phase/sign combinations; no solution |
| E008 | Primes, p−1, integer totients; offsets 0–255; four signs | 168,960 offset/sign combinations; no solution |
| E009 | Full E007/E008 optimization on 39 matched nulls for selected LP2-55/49 | Raw p=0.25/0.95; each Bonferroni55=1 |
| E010 | Ciphertext autokey, periods 1–64, four signs, at least 60 suffix runes | 13,516 variants; global model p=0.464; synthetic control exact |
| E011 | Plaintext autokey, 390 unreduced word keys, four signs, none/all F | 171,600 variants; selected-page p=0.15/0.375, adjusted 1; synthetic control exact |

E007/E008 use exact dynamic programming over all F-interruption subsets within
their fixed grid. Copied F does not consume key material. States merge only
when key cursor and language context agree; there is no beam cutoff. The count
of tasks is not a count of independently tested F masks.
Plaintext-autokey keys must not be reduced to primitive Vigenère cycles.

The trigram backoff model uses alpha=0.5 and strength 5. CIRCUMFERENCE is exact;
DIVINITY has six wrong runes (98.835% accuracy); LP2-56 still chooses the wrong
interruption. Mutation rankings are correlated descriptive diagnostics.
Conditional nulls use independent count-preserving shuffles accepted only when
adjacent-equality counts match, avoiding the accepted-move sampler problem.
Every null repeats the complete relevant search. Thirty-nine nulls cannot
resolve significance after a 55-page correction. E010's Markov simulations do
not preserve exact page frequencies or propagate fitted-q uncertainty.
The full candidate outputs were retained and did not yield coherent plaintext.
**48 tests passed; 550 candidate records were independently recalculated.**
There were 115 completed processes, 361.871 experiment seconds within 900,
maximum 180 per task. Successful inversion confirms a rule, not genuine language.

## Evidence

- [Original frozen report](../../reports/attack_phase2_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase2_summary.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [attack_phase2_complete.json](../../checkpoints/attack_phase2_complete.json).
