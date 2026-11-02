# Phase 22: Longer plaintext-autokey seeds

**No new decryption confirmed.** Historical report date: 2026-10-22T17:45:25.481371+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E062 extends the affine-chain autokey machinery to lengths 4–32 and four sign
pairs: 116 families per input. The rule is
`P[i]=cs*C[i]+ks*P[i-m] mod29` after an unknown initial key; every rune consumes
a step, including F. Eight frequency starts use up to six trigram coordinate
sweeps. A fixed beam of width 128, two cuts, and two retained paths per cut
provides a second branch. Both are fourgram-ranked; twelve distinct starts
receive up to six further sweeps. This remains a heuristic.

All twelve controls recover exactly: six 300-rune cases with lengths
13/23/31/4/8/12, three 200-rune cases with lengths 13/23/31, and three
729-rune cases with lengths 13/23/31. Keys use all 29 symbols and are fresh;
training I and III–IX excludes control chapters X–XII, but those texts are
historically seen. Before final refinement, frequency/beam top candidates
are exact in 11/12 and 12/12 cases respectively; the different budgets do not
support an equal-cost performance claim.

The independent checker detects a null-generation error: E062-null-2 preserves
counts and adjacent matches but not the required endpoints. Its score
-4.352205 and records remain unchanged and are not used as plan-compliant
evidence. A separately registered E062-null-endpoints run uses the same solver
and seed while fixing endpoints; score -4.317967. Only after its verification
does the unknown attack begin. Single diagnostic nulls receive no p-value.

E063 tests 46 pages of at least 200 runes. Nine shorter rune pages and numeric
LP2-50 are explicitly listed as excluded. LP2-02 wins at -3.809125 with seed
length 29, followed by LP2-07/38/33/23. Six of nineteen full matched-null
searches reach it: raw p=0.35, Bonferroni46=1. Each null preserves counts,
endpoints, and adjacent matches and searches every family and refinement.
Nineteen draws cannot resolve corrected significance.

**126 tests passed.** A separate scalar key queue checks source windows,
decryption/inversion, scores, coordinate maxima, seeds, and selection.
Seventy-nine tasks take 497.708 seconds within 2,400, maximum 180 each;
sampled peak 102.7 MiB against 768. Historical results are not rerun unchanged.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Runes | Seed length | Plaintext |
|---|---:|---:|---|
| 0 | 300 | 13 | exact |
| 1 | 300 | 23 | exact |
| 2 | 300 | 31 | exact |
| 3 | 300 | 4 | exact |
| 4 | 300 | 8 | exact |
| 5 | 300 | 12 | exact |
| 6 | 200 | 13 | exact |
| 7 | 200 | 23 | exact |
| 8 | 200 | 31 | exact |
| 9 | 729 | 13 | exact |
| 10 | 729 | 23 | exact |
| 11 | 729 | 31 | exact |

| Page | Runes | Recovered seed length | Score |
|---|---:|---:|---:|
| LP2-02 | 201 | 29 | -3.809125 |
| LP2-07 | 208 | 31 | -3.919218 |
| LP2-38 | 228 | 32 | -3.937625 |
| LP2-33 | 214 | 31 | -3.940715 |
| LP2-23 | 213 | 32 | -3.969634 |

## Evidence

- [Original frozen report](../../reports/attack_phase22_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase22_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase22_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [autokey_extended_plan.json](../../experiments/autokey_extended_plan.json), [autokey_endpoint_null_plan.json](../../experiments/autokey_endpoint_null_plan.json), [autokey_extended_unknown_plan.json](../../experiments/autokey_extended_unknown_plan.json), [phase22_summary.json](../../results/phase22_summary.json), [phase22_complete.json](../../checkpoints/phase22_complete.json).
