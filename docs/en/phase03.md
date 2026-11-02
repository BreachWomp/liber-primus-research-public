# Phase 3: Section keys, running text keys, and short autokey

**No new decryption confirmed.** Historical report date: 2026-10-19.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

| Experiment | Search | Outcome |
|---|---|---|
| E012 | Ten source-based section hypotheses; primes, p−1, totients; offsets 0–255; four signs; exact F subsets | LP2-00–02 raw p=0.10, group-adjusted 1 |
| E013 | All valid starts in 41,522 runes of Emerson's Self-Reliance; two encodings; four signs; none/all F | 36,336,608 variants; LP2-49 p=0.125, adjusted 1 |
| E014 | All 1–3-rune initial keys; four signs; none/all F; 55 pages | 11,113,960 variants; LP2-55 p=0.375, adjusted 1 |
| E015 | `P[i]=a*(C[i]-C[i-1])+b mod29`, all 812 invertible affine maps | 44,660 variants; global model p=0.48 |

Section boundaries come from pinned sources, including their alternative
treatment of LP2-54/55. No section was trimmed after observing its score.
LP2-50 occupies a zero-width rune span; zero key consumption there is a model
assumption. The running key is thematic speculation, not an established Cicada
key. Two explicit Q encodings were tried; omitted non-ASCII letters were
inventoried. Original Gutenberg bytes, including notices, remain unchanged.

The synthetic continuous-section rule reproduces its source exactly, but the
E012 scorer selects F48 instead of F49 and reaches only 99.373% accuracy.
Automatic decryption claims remain blocked. E013–E015 each recover their
synthetic control as the best output. E013/E014 use 39 exact-frequency and
adjacent-equality nulls, each fully optimized. E012 uses 39 Markov simulations;
E015 uses 199 and maximizes over all pages/maps in each. The latter nulls do not
fix observed frequencies or propagate q uncertainty. All four additionally
adjusted diagnostic p-values are 1.

**57 tests passed; 418 saved candidate records were independently rescored and
re-encrypted.** Sixteen successful processes took 451.791 experiment seconds
within a 900-second budget. One control was accidentally rerun because `180`
and `180.0` produced different fingerprints. Both events and their runtime are
retained; they are not two independent controls.

## Evidence

- [Original frozen report](../../reports/attack_phase3_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase3_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase3_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [emerson_manifest.json](../../sources/emerson_manifest.json), [phase3_complete.json](../../checkpoints/phase3_complete.json).
