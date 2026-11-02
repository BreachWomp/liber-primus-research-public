# Phase 25: Both feedback coefficients and fresh null calibration

**No new decryption confirmed.** Historical report date: 2026-10-25T17:26:01.790412+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E068 expands to `P[i]=a*C[i]+b*P[i-m] mod29`, a,b=1–28, m=4–32.
There are 22,736 families per input; eight of 784 pairs per length are retained
for 232 heuristic optimizations. Histogram screening exploits multiplication
as a permutation of prefix values. A separate direct-symbol calculation checks
scores within 1e-7; ranking rounds to nine decimals with fixed ties. A larger
parameter grid need not improve each score because screening may discard old
families and new seeds may find different local optima.

All sixteen controls recover text, key, and coefficients exactly: twelve fresh
keys on previously seen excluded-source windows and four E066 regression
inputs rerun with the changed search. All injected families rank first. One
diagnostic full null scores -4.263207. E069 attacks 46 pages and ten groups,
56 input hypotheses covering all unknown rune pages. LP2-02 wins at
-3.6266635094642607, m=32,a=24,b=13. The initial nineteen full matched nulls
have zero exceedances, giving raw p=0.05 but adjusted p=1.

E070 is separately registered with **99 fresh nulls**. Five reach the frozen
score: plus-one p=0.06, Bonferroni56=1. The first nineteen are not pooled into
an adaptively stopped p-value. Every null preserves per-page counts, endpoints,
and adjacent matches and repeats all screening and refinement. Even zero
exceedances among 99 could only reach adjusted p=0.56, so this remains a coarse
screen. The historical interim report correctly labels its then-pending
validation and unstarted follow-up; its wording has not been rewritten.

**131 tests passed.** Separate verification covers all 732,540 language-table
entries, sequence scores at six lengths/two orders, direct family scoring,
inverse queues, coordinate maxima, transitions, and 354,496 starting prefixes.
All 784 coefficient pairs are tested at two delays. There are 191 registered
tasks, 3,004.272 experiment seconds within 3,600, sampled peak 165.0 MiB against
768, maximum 180 per task and one worker. Successful controls do not prove
complete search over every key, text type, or boundary convention.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Runes | m | a | b | Screening rank | Outcome |
|---|---:|---:|---:|---:|---:|---|
| 0 | 200 | 13 | 2 | 3 | 1 | exact |
| 1 | 200 | 23 | 7 | 8 | 1 | exact |
| 2 | 200 | 31 | 14 | 15 | 1 | exact |
| 3 | 300 | 13 | 27 | 3 | 1 | exact |
| 4 | 300 | 23 | 2 | 8 | 1 | exact |
| 5 | 300 | 31 | 7 | 15 | 1 | exact |
| 6 | 729 | 13 | 14 | 3 | 1 | exact |
| 7 | 729 | 23 | 27 | 8 | 1 | exact |
| 8 | 729 | 31 | 2 | 15 | 1 | exact |
| 9 | 3316 | 13 | 7 | 3 | 1 | exact |
| 10 | 3316 | 23 | 14 | 8 | 1 | exact |
| 11 | 3316 | 32 | 27 | 15 | 1 | exact |
| 12 | 200 | 31 | 1 | 14 | 1 | exact |
| 13 | 300 | 31 | 28 | 7 | 1 | exact |
| 14 | 729 | 31 | 1 | 2 | 1 | exact |
| 15 | 3316 | 31 | 28 | 27 | 1 | exact |

| Input | Runes | m | a | b | Score |
|---|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 32 | 13 | 11 | -4.080898 |
| LP2-01 | 266 | 32 | 7 | 13 | -4.168375 |
| LP2-02 | 201 | 32 | 24 | 13 | -3.626664 |
| LP2-03 | 217 | 31 | 16 | 13 | -3.906549 |
| LP2-04 | 261 | 29 | 13 | 11 | -4.110637 |
| LP2-05 | 263 | 32 | 21 | 11 | -4.152556 |
| LP2-07 | 208 | 30 | 2 | 14 | -3.753534 |
| LP2-08 | 255 | 32 | 18 | 3 | -4.088323 |
| LP2-09 | 268 | 32 | 14 | 23 | -4.222930 |
| LP2-10 | 263 | 32 | 1 | 18 | -4.051974 |
| LP2-11 | 273 | 32 | 25 | 8 | -4.101359 |
| LP2-12 | 261 | 32 | 1 | 4 | -4.070675 |
| LP2-13 | 272 | 32 | 17 | 6 | -4.167353 |
| LP2-16 | 267 | 32 | 27 | 4 | -4.218172 |
| LP2-17 | 273 | 31 | 22 | 7 | -4.164952 |
| LP2-18 | 260 | 31 | 14 | 26 | -3.972368 |
| LP2-19 | 271 | 32 | 21 | 7 | -4.106423 |
| LP2-20 | 269 | 32 | 9 | 9 | -4.206273 |
| LP2-21 | 273 | 32 | 25 | 5 | -4.097373 |
| LP2-23 | 213 | 31 | 8 | 17 | -3.868836 |
| LP2-24 | 270 | 32 | 23 | 10 | -4.131706 |
| LP2-25 | 273 | 32 | 2 | 11 | -4.199825 |
| LP2-26 | 265 | 32 | 27 | 4 | -4.214270 |
| LP2-27 | 234 | 32 | 22 | 22 | -3.951126 |
| LP2-28 | 269 | 31 | 14 | 3 | -4.188659 |
| LP2-29 | 277 | 30 | 14 | 3 | -4.140196 |
| LP2-30 | 263 | 32 | 7 | 6 | -4.142521 |
| LP2-31 | 269 | 32 | 10 | 24 | -4.171938 |
| LP2-33 | 214 | 32 | 7 | 14 | -3.776675 |
| LP2-34 | 261 | 30 | 21 | 5 | -4.043842 |
| LP2-35 | 271 | 31 | 14 | 7 | -4.188216 |
| LP2-36 | 238 | 30 | 16 | 4 | -3.973433 |
| LP2-37 | 228 | 31 | 4 | 6 | -3.945966 |
| LP2-38 | 228 | 32 | 9 | 22 | -3.866804 |
| LP2-39 | 240 | 32 | 26 | 17 | -3.990545 |
| LP2-40 | 231 | 32 | 25 | 22 | -3.945449 |
| LP2-41 | 273 | 31 | 26 | 8 | -4.147062 |
| LP2-42 | 272 | 32 | 10 | 7 | -4.155618 |
| LP2-43 | 274 | 32 | 13 | 19 | -4.201716 |
| LP2-44 | 273 | 32 | 12 | 4 | -4.255692 |
| LP2-45 | 270 | 32 | 1 | 26 | -4.259561 |
| LP2-46 | 270 | 32 | 27 | 23 | -4.186894 |
| LP2-47 | 274 | 32 | 23 | 6 | -4.223040 |
| LP2-48 | 271 | 32 | 23 | 6 | -4.189409 |
| LP2-52 | 263 | 32 | 26 | 19 | -4.171327 |
| LP2-54 | 232 | 32 | 21 | 7 | -3.941735 |
| LP2-00_02 | 729 | 31 | 4 | 27 | -5.290033 |
| LP2-03_07 | 1145 | 32 | 15 | 14 | -5.639260 |
| LP2-08_14 | 1729 | 32 | 4 | 16 | -5.885758 |
| LP2-15_22 | 1903 | 32 | 15 | 4 | -5.939762 |
| LP2-23_26 | 1021 | 32 | 7 | 21 | -5.563707 |
| LP2-27_32 | 1433 | 32 | 21 | 15 | -5.821308 |
| LP2-33_39 | 1680 | 32 | 7 | 25 | -5.924589 |
| LP2-40_53 | 3008 | 32 | 8 | 5 | -6.192441 |
| LP2-54_55 | 308 | 30 | 19 | 10 | -4.377280 |
| LP2-40_55 | 3316 | 32 | 22 | 19 | -6.225445 |

## Evidence

- [Original frozen report](../../reports/attack_phase25_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase25_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase25_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [bilinear_feedback_plan.json](../../experiments/bilinear_feedback_plan.json), [bilinear_feedback_unknown_plan.json](../../experiments/bilinear_feedback_unknown_plan.json), [bilinear_feedback_more_null_plan.json](../../experiments/bilinear_feedback_more_null_plan.json), [phase25_summary.json](../../results/phase25_summary.json), [phase25_complete.json](../../checkpoints/phase25_complete.json).

[English candidate appendix](phase25_candidates.md).
