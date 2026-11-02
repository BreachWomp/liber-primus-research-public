# Phase 27: Delay-three feedback with exact retained-family prefixes

**No new decryption confirmed.** Historical report date: 2026-11-01T09:06:01.671314+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E074/E075 test `P[i]=a*C[i]+b*P[i-3]+c mod29`, a,b=1–28,c=0–28.
Unigram screening ranks 22,736 families and keeps sixteen. For each retained
family, all 29^3=24,389 initial prefixes are scored with the fixed external
fourgram model. Prefix search is exact; family selection is heuristic. No
runes are omitted and there are no hidden resets.

E074 compares 73,167 prefix scores with a separate scalar recurrence. Its
longest throughput test, 3,316 random runes, takes about 36 seconds. Twelve
new short controls use 66/95/200/300 runes; four c=0 controls use
200/300/729/3,316 and earlier sign pairs. All sixteen recover text, key, and
coefficients exactly, with injected family rank one. Keys are new, but source
windows are previously seen and partly nested. One diagnostic null scores
-5.079480 without a p-value.

E076 attacks all 55 unknown rune pages individually, including short pages.
LP2-50 remains in the plan with original numeric content and exclusion reason.
Source layouts and ten source-file hashes are checked. LP2-55 wins at -4.709924,
a=8,b=3,c=3. One of nineteen full matched-null searches reaches it: raw p=0.10,
Bonferroni55=1. Counts, endpoints, and adjacent matches are preserved. With
nineteen nulls, corrected significance cannot be resolved.

A separate queue implementation, without the production affine formula,
recomputes **35,900,608 prefix scores across 92 runs**, including whole-vector
hashes. Retained-family optima, candidate inverses, sources, seeds, nulls,
selection, and scalar model probabilities are checked. The complete unigram
screen is reproduced, while only retained and control families receive direct
independent screening checks. The 22,720 discarded families remain unsearched
at the exact-prefix stage; the cipher class is not excluded.

**138 tests passed; 92 tasks; 349.583 experiment seconds within 1,800.** Sampled
peak 134.6 MiB against 768, one worker. Validation time is recorded separately.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Runes | a | b | c | Screening rank | Outcome |
|---|---:|---:|---:|---:|---:|---|
| 0 | 66 | 2 | 1 | 2 | 1 | exact |
| 1 | 66 | 7 | 3 | 7 | 1 | exact |
| 2 | 66 | 14 | 15 | 12 | 1 | exact |
| 3 | 95 | 27 | 28 | 17 | 1 | exact |
| 4 | 95 | 2 | 1 | 22 | 1 | exact |
| 5 | 95 | 7 | 3 | 27 | 1 | exact |
| 6 | 200 | 14 | 15 | 4 | 1 | exact |
| 7 | 200 | 27 | 28 | 9 | 1 | exact |
| 8 | 200 | 2 | 1 | 14 | 1 | exact |
| 9 | 300 | 7 | 3 | 19 | 1 | exact |
| 10 | 300 | 14 | 15 | 24 | 1 | exact |
| 11 | 300 | 27 | 28 | 1 | 1 | exact |
| 12 | 200 | 1 | 1 | 0 | 1 | exact |
| 13 | 300 | 1 | 28 | 0 | 1 | exact |
| 14 | 729 | 28 | 1 | 0 | 1 | exact |
| 15 | 3316 | 28 | 28 | 0 | 1 | exact |

| Page | Runes | a | b | c | Score |
|---|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 19 | 12 | 20 | -5.841415 |
| LP2-01 | 266 | 8 | 20 | 8 | -5.949304 |
| LP2-02 | 201 | 2 | 7 | 3 | -5.613873 |
| LP2-03 | 217 | 3 | 16 | 28 | -5.729440 |
| LP2-04 | 261 | 4 | 14 | 24 | -5.844781 |
| LP2-05 | 263 | 24 | 24 | 21 | -5.879382 |
| LP2-06 | 196 | 1 | 20 | 0 | -5.575591 |
| LP2-07 | 208 | 3 | 11 | 25 | -5.822003 |
| LP2-08 | 255 | 23 | 10 | 0 | -5.926910 |
| LP2-09 | 268 | 24 | 26 | 1 | -5.927997 |
| LP2-10 | 263 | 17 | 12 | 22 | -5.895116 |
| LP2-11 | 273 | 21 | 8 | 3 | -5.827590 |
| LP2-12 | 261 | 20 | 3 | 15 | -5.967409 |
| LP2-13 | 272 | 4 | 15 | 25 | -5.885759 |
| LP2-14 | 137 | 8 | 5 | 22 | -5.437004 |
| LP2-15 | 159 | 21 | 17 | 16 | -5.637875 |
| LP2-16 | 267 | 12 | 25 | 9 | -5.664610 |
| LP2-17 | 273 | 6 | 15 | 20 | -5.866045 |
| LP2-18 | 260 | 14 | 7 | 14 | -5.926975 |
| LP2-19 | 271 | 9 | 7 | 9 | -5.873445 |
| LP2-20 | 269 | 21 | 15 | 18 | -5.873747 |
| LP2-21 | 273 | 24 | 25 | 26 | -5.872333 |
| LP2-22 | 131 | 13 | 24 | 5 | -5.389070 |
| LP2-23 | 213 | 9 | 4 | 22 | -5.680699 |
| LP2-24 | 270 | 17 | 2 | 4 | -5.867857 |
| LP2-25 | 273 | 26 | 26 | 9 | -5.915938 |
| LP2-26 | 265 | 14 | 5 | 4 | -5.940363 |
| LP2-27 | 234 | 26 | 16 | 22 | -5.818414 |
| LP2-28 | 269 | 21 | 16 | 21 | -5.846769 |
| LP2-29 | 277 | 12 | 18 | 7 | -5.940384 |
| LP2-30 | 263 | 17 | 28 | 18 | -5.936974 |
| LP2-31 | 269 | 20 | 10 | 21 | -5.951627 |
| LP2-32 | 121 | 22 | 10 | 19 | -5.465029 |
| LP2-33 | 214 | 9 | 16 | 26 | -5.833597 |
| LP2-34 | 261 | 2 | 14 | 21 | -5.841120 |
| LP2-35 | 271 | 27 | 19 | 13 | -5.893688 |
| LP2-36 | 238 | 25 | 6 | 0 | -5.830767 |
| LP2-37 | 228 | 14 | 11 | 23 | -5.862702 |
| LP2-38 | 228 | 20 | 8 | 12 | -5.756881 |
| LP2-39 | 240 | 3 | 23 | 20 | -5.891836 |
| LP2-40 | 231 | 9 | 20 | 8 | -5.860458 |
| LP2-41 | 273 | 1 | 7 | 13 | -5.862887 |
| LP2-42 | 272 | 22 | 19 | 16 | -6.006777 |
| LP2-43 | 274 | 22 | 14 | 17 | -5.923317 |
| LP2-44 | 273 | 22 | 14 | 0 | -5.971032 |
| LP2-45 | 270 | 9 | 1 | 6 | -5.948426 |
| LP2-46 | 270 | 17 | 15 | 25 | -5.975992 |
| LP2-47 | 274 | 3 | 1 | 21 | -5.896238 |
| LP2-48 | 271 | 11 | 13 | 12 | -5.848145 |
| LP2-49 | 66 | 17 | 18 | 20 | -4.762790 |
| LP2-51 | 92 | 9 | 22 | 16 | -5.086863 |
| LP2-52 | 263 | 9 | 9 | 10 | -5.894641 |
| LP2-53 | 179 | 8 | 28 | 11 | -5.621518 |
| LP2-54 | 232 | 28 | 13 | 6 | -5.862804 |
| LP2-55 | 76 | 8 | 3 | 3 | -4.709924 |

## Evidence

- [Original frozen report](../../reports/attack_phase27_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase27_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase27_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [delay_three_plan.json](../../experiments/delay_three_plan.json), [delay_three_unknown_plan.json](../../experiments/delay_three_unknown_plan.json), [phase27_summary.json](../../results/phase27_summary.json).

[English candidate appendix](phase27_candidates.md).
