# Phase 21: Constrained fragment phases and a hybrid initializer

**No new decryption confirmed.** Historical report date: 2026-10-22T17:22:58.761128+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E058 uses exact chain DP to constrain fragment phases by
`phase_b-phase_a=(b-a)-s mod m`, with s bounded by ciphertext F count in the
gap. Gaps contribute cursor possibilities but no pool language score. Pages
remain separate chains. Lengths 17–32, bounded starts, and the carried E056
context remain unchanged. Fresh windows are 16000:16729 in Emerson X–XII.
After Stage A passes, remaining regressions/stress cases run. E058 alone is
**17/18 exact**, failing the older 1,200-rune length-31 case at 49/1,200.
Its planned unknown attack **E059 remains unrun**.

E060 combines the unchanged E057 and E058 searches and merges their top three
outputs using the same full-text score, deterministic ties, and deduplicated
plaintext. Previously completed searches are reused only when ciphertext,
page spans, training, code, outputs, and validation hashes match. Controls do
not choose which branch is enabled. Three fresh 729-rune windows at
16850:17579 plus difficult regressions and the remaining controls give
**21/21 exact** texts, keys, signs, phases, and masks. These adjacent source
windows are not independent new corpora. A full diagnostic null scores
-5.476413. For the hard case, constrained phase assignments are fewer by a
calculated factor 119,536,775.5; this is a combinatorial count, not measured
runtime acceleration. The true key emerges only in later refinement.

E061 attacks nine groups covering all 55 unknown rune pages with shared keys,
independent page phases, optional F copies, and continuous language context.
LP2-50 remains an empty span. LP2-00_02 wins at -5.538402, primitive length 31.
Thirteen of nineteen full matched-null optimizations reach it: raw p=0.70,
Bonferroni9=1. Nulls preserve per-page counts, endpoints, and adjacent matches.
Initial-F ambiguity alternatives stay visible. No solution is supported.

**124 tests passed**, including exhaustive small phase chains, scalar states,
an independent backward chain recurrence, inverses, sources, and nulls.
Sixty-nine tasks use 2,041.652 experiment seconds. Before E060 the overall
budget was prospectively raised to 3,600 seconds; E058 kept its original limit.
An interruption reused thirteen completed hash-verified tasks and reran only
the unfinished fifth null and missing successors. A conservative 185-second
allowance covers the unmeasured aborted run, without presenting it as measured
time. Sampled peak memory 162.9 MiB against 768, one worker.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Key | Runes | Text/key/sign/mask/phases |
|---|---:|---:|---|
| regression 0 | 31 | 729 | exact |
| regression 14 | 31 | 1200 | exact |
| fresh 0 | 17 | 729 | exact |
| fresh 1 | 23 | 729 | exact |
| fresh 2 | 31 | 729 | exact |
| regression 1 | 17 | 729 | exact |
| regression 2 | 23 | 729 | exact |
| regression 3 | 31 | 729 | exact |
| regression 4 | 17 | 729 | exact |
| regression 5 | 23 | 729 | exact |
| regression 6 | 17 | 3316 | exact |
| regression 7 | 23 | 3316 | exact |
| regression 8 | 31 | 3316 | exact |
| regression 9 | 17 | 1200 | exact |
| regression 10 | 23 | 1200 | exact |
| regression 11 | 31 | 1200 | exact |
| regression 12 | 17 | 3316 | exact |
| regression 13 | 23 | 1200 | exact |
| regression 15 | 17 | 729 | exact |
| regression 16 | 23 | 729 | exact |
| regression 17 | 31 | 729 | exact |

| Section | Runes | Recovered primitive key length | Best score |
|---|---:|---:|---:|
| LP2-00_02 | 729 | 31 | -5.538402 |
| LP2-03_07 | 1145 | 31 | -5.759327 |
| LP2-08_14 | 1729 | 32 | -5.929138 |
| LP2-15_22 | 1903 | 31 | -5.961106 |
| LP2-23_26 | 1021 | 30 | -5.638826 |
| LP2-27_32 | 1433 | 28 | -5.843719 |
| LP2-33_39 | 1680 | 31 | -5.940864 |
| LP2-40_53 | 3008 | 25 | -6.072220 |
| LP2-40_55 | 3316 | 32 | -6.103820 |

## Evidence

- [Original frozen report](../../reports/attack_phase21_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase21_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase21_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [constrained_fragment_plan.json](../../experiments/constrained_fragment_plan.json), [hybrid_fragment_plan.json](../../experiments/hybrid_fragment_plan.json), [hybrid_unknown_plan.json](../../experiments/hybrid_unknown_plan.json), [phase21_summary.json](../../results/phase21_summary.json), [phase21_complete.json](../../checkpoints/phase21_complete.json).
