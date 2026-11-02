# Phase 26: An additive constant in delayed feedback

**No new decryption confirmed.** Historical report date: 2026-10-31T12:14:43.995412+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

The rule is `P[i]=a*C[i]+b*P[i-m]+c mod29`, a,b=1–28,c=0–28,m=4–32.
The inverse uses a^-1; initial key values use b^-1. For b≠1, shifting by
`d=c/(1-b)` gives the affine representation; for b=1 the additive term is
`q*c`, q=floor(i/m). Both must enter language scoring. These constants were
not already covered by c=0, but the algebra itself is established.

E071 checks 27,608 families with separate direct queues, maximum discrepancy
1.14e-13. Full screening on 3,316 synthetic runes takes 3.963 seconds. Per
input, 659,344 families are scored and eight per delay retained for 232
heuristic optimizations plus twelve final refinements. E072 passes all sixteen
controls, including four fresh b=1 cases and four c=0 regressions. These use
new keys/constants on previously seen excluded-source blocks, not sixteen
unknown texts. A diagnostic null scores -4.318019.

E073 tests 46 pages and ten continuous-state groups. LP2-02 wins at -3.664221,
m=31,a=19,b=23,c=2. Three of nineteen fully optimized matched nulls reach it:
raw p=0.20, Bonferroni56=1. All 56 research-page source anchors and ten pinned
source-file hashes are checked; numeric LP2-50 stays present. Nulls preserve
counts, endpoints, and adjacent matches. No linguistic evidence beyond this
null comparison supports the candidate.

The checker independently reconstructs retained/control families, scores,
inverse queues, seeds, and page state. All 732,540 model entries are separately
validated. The complete screening grid is reproduced with production code;
that is replication, **not a second independent full-grid implementation**.
E071 supplies the independent synthetic-family check. Only eight families per
delay survive, and English-prose scoring can miss other plaintext types.

**136 tests passed; 93 tasks; 1,983.962 seconds within 3,600.** Sampled peak
139.4 MiB against 768 for E072/E073. E071 had a cooperative 120-second cap and
bounded arrays but no recorded OS-level memory peak. A filename collision with
the historical E019 plan/test was discovered and restored byte-for-byte from
Git. The actual E072 plan/runner bytes are archived separately, with the
[path migration record](../../checkpoints/phase26_path_migration.json).
No old result or log event was rewritten.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Runes | m | a | b | c | Screening rank | Outcome |
|---|---:|---:|---:|---:|---:|---:|---|
| 0 | 200 | 13 | 2 | 1 | 2 | 1 | exact |
| 1 | 200 | 23 | 7 | 3 | 7 | 1 | exact |
| 2 | 200 | 31 | 14 | 15 | 12 | 3 | exact |
| 3 | 300 | 13 | 27 | 1 | 17 | 1 | exact |
| 4 | 300 | 23 | 2 | 3 | 22 | 1 | exact |
| 5 | 300 | 31 | 7 | 15 | 27 | 1 | exact |
| 6 | 729 | 13 | 14 | 1 | 4 | 1 | exact |
| 7 | 729 | 23 | 27 | 3 | 9 | 1 | exact |
| 8 | 729 | 31 | 2 | 15 | 14 | 1 | exact |
| 9 | 3316 | 13 | 7 | 1 | 19 | 1 | exact |
| 10 | 3316 | 23 | 14 | 3 | 24 | 1 | exact |
| 11 | 3316 | 32 | 27 | 15 | 1 | 1 | exact |
| 12 | 200 | 13 | 2 | 3 | 0 | 1 | exact |
| 13 | 300 | 13 | 27 | 3 | 0 | 1 | exact |
| 14 | 729 | 13 | 14 | 3 | 0 | 1 | exact |
| 15 | 3316 | 32 | 27 | 15 | 0 | 1 | exact |

| Input | Runes | m | a | b | c | Score |
|---|---:|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 32 | 9 | 7 | 9 | -4.049275 |
| LP2-01 | 266 | 32 | 27 | 10 | 23 | -4.079168 |
| LP2-02 | 201 | 31 | 19 | 23 | 2 | -3.664221 |
| LP2-03 | 217 | 31 | 1 | 22 | 24 | -3.817342 |
| LP2-04 | 261 | 30 | 26 | 16 | 14 | -4.110784 |
| LP2-05 | 263 | 32 | 11 | 27 | 22 | -4.115219 |
| LP2-07 | 208 | 32 | 1 | 2 | 5 | -3.698106 |
| LP2-08 | 255 | 31 | 27 | 2 | 10 | -4.032793 |
| LP2-09 | 268 | 32 | 19 | 15 | 25 | -4.046354 |
| LP2-10 | 263 | 31 | 19 | 3 | 28 | -4.097870 |
| LP2-11 | 273 | 32 | 19 | 11 | 21 | -4.211309 |
| LP2-12 | 261 | 32 | 13 | 6 | 11 | -4.131152 |
| LP2-13 | 272 | 32 | 8 | 5 | 16 | -4.134329 |
| LP2-16 | 267 | 32 | 18 | 16 | 25 | -3.983963 |
| LP2-17 | 273 | 29 | 21 | 3 | 6 | -4.186698 |
| LP2-18 | 260 | 31 | 13 | 2 | 26 | -3.973263 |
| LP2-19 | 271 | 32 | 28 | 11 | 9 | -4.215476 |
| LP2-20 | 269 | 32 | 3 | 4 | 25 | -4.087657 |
| LP2-21 | 273 | 32 | 24 | 27 | 11 | -4.178508 |
| LP2-23 | 213 | 31 | 2 | 7 | 24 | -3.744365 |
| LP2-24 | 270 | 32 | 9 | 15 | 7 | -4.112038 |
| LP2-25 | 273 | 31 | 4 | 14 | 11 | -4.208061 |
| LP2-26 | 265 | 29 | 7 | 6 | 21 | -4.181734 |
| LP2-27 | 234 | 32 | 11 | 9 | 15 | -3.869667 |
| LP2-28 | 269 | 32 | 4 | 8 | 15 | -4.076173 |
| LP2-29 | 277 | 30 | 20 | 22 | 26 | -4.242052 |
| LP2-30 | 263 | 31 | 21 | 5 | 15 | -4.040406 |
| LP2-31 | 269 | 32 | 11 | 2 | 9 | -4.145374 |
| LP2-33 | 214 | 31 | 7 | 5 | 8 | -3.866210 |
| LP2-34 | 261 | 32 | 15 | 25 | 17 | -4.136165 |
| LP2-35 | 271 | 32 | 25 | 27 | 20 | -4.175975 |
| LP2-36 | 238 | 32 | 11 | 15 | 13 | -3.926530 |
| LP2-37 | 228 | 31 | 27 | 15 | 28 | -3.891313 |
| LP2-38 | 228 | 32 | 25 | 16 | 9 | -3.977079 |
| LP2-39 | 240 | 31 | 28 | 21 | 10 | -4.005729 |
| LP2-40 | 231 | 29 | 1 | 24 | 1 | -3.941308 |
| LP2-41 | 273 | 31 | 4 | 18 | 19 | -4.149683 |
| LP2-42 | 272 | 30 | 22 | 4 | 18 | -4.186535 |
| LP2-43 | 274 | 31 | 25 | 19 | 13 | -4.210248 |
| LP2-44 | 273 | 30 | 14 | 14 | 10 | -4.171097 |
| LP2-45 | 270 | 31 | 10 | 20 | 5 | -4.169674 |
| LP2-46 | 270 | 32 | 3 | 6 | 25 | -4.224878 |
| LP2-47 | 274 | 32 | 8 | 2 | 18 | -4.174121 |
| LP2-48 | 271 | 32 | 7 | 23 | 13 | -4.130169 |
| LP2-52 | 263 | 30 | 27 | 7 | 2 | -4.176117 |
| LP2-54 | 232 | 31 | 27 | 2 | 9 | -3.904587 |
| LP2-00_02 | 729 | 32 | 2 | 2 | 2 | -5.266653 |
| LP2-03_07 | 1145 | 32 | 14 | 3 | 25 | -5.613541 |
| LP2-08_14 | 1729 | 32 | 23 | 4 | 24 | -5.910717 |
| LP2-15_22 | 1903 | 31 | 24 | 16 | 22 | -5.956971 |
| LP2-23_26 | 1021 | 31 | 16 | 4 | 6 | -5.545311 |
| LP2-27_32 | 1433 | 32 | 18 | 26 | 19 | -5.747922 |
| LP2-33_39 | 1680 | 31 | 25 | 20 | 20 | -5.894594 |
| LP2-40_53 | 3008 | 32 | 5 | 6 | 23 | -6.159527 |
| LP2-54_55 | 308 | 32 | 21 | 9 | 9 | -4.257299 |
| LP2-40_55 | 3316 | 32 | 28 | 13 | 3 | -6.196766 |

## Evidence

- [Original frozen report](../../reports/attack_phase26_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase26_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase26_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [phase26_path_migration.json](../../checkpoints/phase26_path_migration.json), [delayed_affine_feedback_plan.json](../../experiments/delayed_affine_feedback_plan.json), [affine_feedback_unknown_plan.json](../../experiments/affine_feedback_unknown_plan.json), [phase26_summary.json](../../results/phase26_summary.json).

[English candidate appendix](phase26_candidates.md).
