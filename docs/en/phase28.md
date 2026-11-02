# Phase 28: Delay-two feedback with an affine constant

**No new decryption confirmed.** Historical report date: 2026-11-01T17:40:19.248411+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E077–E079 test `P[i]=a*C[i]+b*P[i-2]+c mod29`, a,b=1–28,c=0–28.
Nonzero c is the new target; c=0 remains for controls and identical conditions.
Unigram ranking of 22,736 families uses nine-decimal rounding and stable
lexicographic ties. The best 128 receive exact enumeration of 841 initial
pairs: 107,648 prefixes per input. Family selection remains heuristic.

E077 checks 2,523 scores against separate scalar recurrence, maximum error
3.33e-16. A 256-family/277-rune pilot takes 2.451 seconds. Linear estimates of
217.7 seconds per full grid and 3.33 hours for 55 equal-length inputs exclude
null calibration and are **estimates, not executed full-grid results**. The
frozen 128-family search takes 14.536 seconds on 3,316 random runes.
E078 passes sixteen controls: twelve short nonzero-c cases and four c=0
regressions, with new two-rune keys on previously seen, partly nested source
windows. All text, key, and coefficient values are exact. One null scores
-5.259722 as a diagnostic only.

E079 attacks all 55 unknown rune pages, retaining LP2-50's numeric content
without claiming to decrypt it. LP2-49 wins at -4.842199, a=1,b=22,c=2,
initial queue [2,4]. Ten of nineteen fully optimized matched nulls reach it:
raw p=0.55, Bonferroni55=1. Nulls preserve counts, endpoints, and adjacent
matches; selection hashes are frozen first. Lower-ranked outputs in the
candidate appendix are not additional independent evidence.

A separate queue implementation checks **9,903,616 prefix scores in 92 tasks**
and whole-vector hashes, plus retained-family optima, inverses, source anchors,
seeds, nulls, selection, and model probabilities. Full screening is replicated
with production code; retained/control families get direct independent checks.
The 22,608 discarded families remain outside exact-prefix search. The result
does not rule out the class or non-English/nonlinguistic plaintext.

**140 tests passed; 92 tasks; 193.279 seconds within 1,800.** Sampled peak
146.9 MiB against 768, one worker. Historical results remain unchanged.

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
| LP2-00 | 262 | 5 | 13 | 11 | -5.982003 |
| LP2-01 | 266 | 19 | 24 | 4 | -5.971403 |
| LP2-02 | 201 | 28 | 23 | 17 | -5.792250 |
| LP2-03 | 217 | 3 | 20 | 26 | -5.811031 |
| LP2-04 | 261 | 21 | 27 | 17 | -6.015285 |
| LP2-05 | 263 | 11 | 18 | 23 | -6.004989 |
| LP2-06 | 196 | 19 | 14 | 0 | -5.801196 |
| LP2-07 | 208 | 10 | 12 | 4 | -5.827443 |
| LP2-08 | 255 | 4 | 4 | 1 | -5.969892 |
| LP2-09 | 268 | 22 | 22 | 25 | -5.862787 |
| LP2-10 | 263 | 3 | 8 | 25 | -5.897389 |
| LP2-11 | 273 | 17 | 9 | 22 | -5.937981 |
| LP2-12 | 261 | 9 | 22 | 15 | -5.966786 |
| LP2-13 | 272 | 28 | 15 | 9 | -5.979678 |
| LP2-14 | 137 | 9 | 18 | 15 | -5.511612 |
| LP2-15 | 159 | 10 | 27 | 2 | -5.703918 |
| LP2-16 | 267 | 3 | 27 | 11 | -6.046390 |
| LP2-17 | 273 | 16 | 25 | 24 | -5.972429 |
| LP2-18 | 260 | 6 | 2 | 6 | -5.990088 |
| LP2-19 | 271 | 20 | 3 | 24 | -5.986898 |
| LP2-20 | 269 | 14 | 14 | 15 | -5.951740 |
| LP2-21 | 273 | 21 | 15 | 17 | -5.873837 |
| LP2-22 | 131 | 21 | 10 | 11 | -5.367048 |
| LP2-23 | 213 | 17 | 4 | 6 | -5.770480 |
| LP2-24 | 270 | 25 | 7 | 3 | -5.996611 |
| LP2-25 | 273 | 15 | 5 | 6 | -5.945961 |
| LP2-26 | 265 | 8 | 11 | 14 | -5.926659 |
| LP2-27 | 234 | 2 | 20 | 14 | -5.891963 |
| LP2-28 | 269 | 18 | 4 | 17 | -5.906398 |
| LP2-29 | 277 | 2 | 12 | 3 | -6.006923 |
| LP2-30 | 263 | 24 | 14 | 9 | -5.999397 |
| LP2-31 | 269 | 14 | 11 | 1 | -5.920545 |
| LP2-32 | 121 | 7 | 28 | 7 | -5.514120 |
| LP2-33 | 214 | 22 | 26 | 10 | -5.879347 |
| LP2-34 | 261 | 16 | 5 | 0 | -5.939484 |
| LP2-35 | 271 | 8 | 7 | 27 | -5.906805 |
| LP2-36 | 238 | 25 | 28 | 21 | -5.879587 |
| LP2-37 | 228 | 22 | 21 | 24 | -5.838135 |
| LP2-38 | 228 | 17 | 25 | 19 | -5.706204 |
| LP2-39 | 240 | 22 | 27 | 14 | -5.976610 |
| LP2-40 | 231 | 17 | 6 | 24 | -5.807474 |
| LP2-41 | 273 | 25 | 4 | 8 | -6.024924 |
| LP2-42 | 272 | 12 | 28 | 14 | -5.962386 |
| LP2-43 | 274 | 23 | 13 | 25 | -5.872074 |
| LP2-44 | 273 | 23 | 2 | 1 | -6.014324 |
| LP2-45 | 270 | 4 | 27 | 20 | -5.942486 |
| LP2-46 | 270 | 24 | 5 | 8 | -5.908525 |
| LP2-47 | 274 | 21 | 27 | 25 | -5.970174 |
| LP2-48 | 271 | 1 | 21 | 26 | -5.928379 |
| LP2-49 | 66 | 1 | 22 | 2 | -4.842199 |
| LP2-51 | 92 | 24 | 21 | 11 | -5.144673 |
| LP2-52 | 263 | 22 | 26 | 28 | -5.975860 |
| LP2-53 | 179 | 16 | 15 | 9 | -5.724536 |
| LP2-54 | 232 | 28 | 6 | 7 | -5.957288 |
| LP2-55 | 76 | 25 | 26 | 21 | -5.145977 |

## Evidence

- [Original frozen report](../../reports/attack_phase28_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase28_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase28_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [delay_two_plan.json](../../experiments/delay_two_plan.json), [delay_two_unknown_plan.json](../../experiments/delay_two_unknown_plan.json), [phase28_summary.json](../../results/phase28_summary.json).

[English candidate appendix](phase28_candidates.md).
