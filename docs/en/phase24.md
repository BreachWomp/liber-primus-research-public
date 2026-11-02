# Phase 24: General plaintext-feedback multipliers

**No new decryption confirmed.** Historical report date: 2026-10-24T19:57:03.785747+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E066/E067 test `P[i]=a*C[i]+b*P[i-m] mod29`, a=±1, b=1–28, m=4–32.
The initial key is derived from the first m plaintext symbols using b's modular
inverse. Chain coefficients are reduced modulo 29 to avoid overflow. This
generalizes earlier searches using established affine algebra.

For each input, 1,624 families receive a maximum-unigram score. Four of 56
coefficient pairs per length are retained; those 116 families receive the
fixed E062 initialization and trigram/fourgram refinement budgets. Screening
and key search are heuristic. E066 passes all sixteen controls: twelve new
keys on previously seen, training-excluded 200/300/729/3,316-rune windows,
plus four old E062 inputs rerun under the changed algorithm. Text, key, and
coefficients are exact; every injected family ranks first. A complete
diagnostic null scores -4.370513 without a p-value.

E067 attacks 46 individual pages of at least 200 runes and ten section
hypotheses, covering all 55 unknown rune pages. Group state is continuous;
numeric LP2-50 remains an empty rune span with sources retained. LP2-33 wins
at -3.805311, m=31,a=-1,b=17. Selection and all 56 output hashes are frozen
before nulls. Two of nineteen full matched-null searches reach it: raw p=0.15,
Bonferroni56=1. Nulls retain per-page counts, endpoints, and adjacent matches.
With nineteen draws, the corrected value cannot be below 1; this is a coarse
screen, not evidence of significance. Postselected language-like fragments
are shown in the English candidate appendix without added spaces or corrections.

**129 tests passed.** Independent queue decoding checks screening, scores,
inverse transforms, coordinate maxima, page transitions, and null generation.
All 85,376 seeded starting prefixes are reconstructed. Tests include all 28
feedback factors on long chains. Ninety-two tasks take 986.144 seconds within
3,000; maximum 180 per task, one worker, sampled peak 113.2 MiB against 768.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Runes | m | a | b | Rank | Outcome |
|---|---:|---:|---:|---:|---:|---|
| 0 | 200 | 13 | 1 | 2 | 1 | exact |
| 1 | 200 | 23 | -1 | 7 | 1 | exact |
| 2 | 200 | 31 | 1 | 14 | 1 | exact |
| 3 | 300 | 13 | -1 | 27 | 1 | exact |
| 4 | 300 | 23 | 1 | 2 | 1 | exact |
| 5 | 300 | 31 | -1 | 7 | 1 | exact |
| 6 | 729 | 13 | 1 | 14 | 1 | exact |
| 7 | 729 | 23 | -1 | 27 | 1 | exact |
| 8 | 729 | 31 | 1 | 2 | 1 | exact |
| 9 | 3316 | 13 | -1 | 7 | 1 | exact |
| 10 | 3316 | 23 | 1 | 14 | 1 | exact |
| 11 | 3316 | 31 | -1 | 27 | 1 | exact |
| 12 | 300 | 13 | 1 | 28 | 1 | exact |
| 13 | 300 | 23 | 1 | 1 | 1 | exact |
| 14 | 300 | 31 | -1 | 28 | 1 | exact |
| 15 | 300 | 4 | -1 | 1 | 1 | exact |

| Input | Runes | m | a | b | Score |
|---|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 32 | 1 | 2 | -4.131477 |
| LP2-01 | 266 | 31 | 1 | 26 | -4.206277 |
| LP2-02 | 201 | 28 | 1 | 16 | -3.851236 |
| LP2-03 | 217 | 31 | -1 | 11 | -3.942263 |
| LP2-04 | 261 | 32 | -1 | 21 | -4.158939 |
| LP2-05 | 263 | 32 | 1 | 2 | -4.178662 |
| LP2-07 | 208 | 32 | -1 | 9 | -3.868290 |
| LP2-08 | 255 | 32 | -1 | 3 | -4.073740 |
| LP2-09 | 268 | 31 | 1 | 22 | -4.254368 |
| LP2-10 | 263 | 32 | 1 | 18 | -4.051974 |
| LP2-11 | 273 | 31 | -1 | 18 | -4.231844 |
| LP2-12 | 261 | 32 | 1 | 4 | -4.070675 |
| LP2-13 | 272 | 30 | -1 | 14 | -4.231557 |
| LP2-16 | 267 | 31 | -1 | 10 | -4.222351 |
| LP2-17 | 273 | 32 | -1 | 18 | -4.235019 |
| LP2-18 | 260 | 30 | 1 | 15 | -4.052775 |
| LP2-19 | 271 | 32 | 1 | 25 | -4.125543 |
| LP2-20 | 269 | 32 | 1 | 14 | -4.190049 |
| LP2-21 | 273 | 31 | -1 | 26 | -4.246181 |
| LP2-23 | 213 | 30 | 1 | 2 | -3.866832 |
| LP2-24 | 270 | 30 | 1 | 7 | -4.150421 |
| LP2-25 | 273 | 32 | 1 | 17 | -4.299808 |
| LP2-26 | 265 | 31 | -1 | 17 | -4.221266 |
| LP2-27 | 234 | 30 | 1 | 22 | -4.064949 |
| LP2-28 | 269 | 32 | 1 | 21 | -4.150839 |
| LP2-29 | 277 | 32 | 1 | 25 | -4.248184 |
| LP2-30 | 263 | 32 | 1 | 20 | -4.175627 |
| LP2-31 | 269 | 32 | 1 | 12 | -4.152636 |
| LP2-33 | 214 | 31 | -1 | 17 | -3.805311 |
| LP2-34 | 261 | 31 | -1 | 2 | -4.185525 |
| LP2-35 | 271 | 31 | -1 | 21 | -4.264313 |
| LP2-36 | 238 | 32 | 1 | 16 | -4.086932 |
| LP2-37 | 228 | 31 | 1 | 10 | -3.901837 |
| LP2-38 | 228 | 31 | -1 | 23 | -4.000890 |
| LP2-39 | 240 | 30 | 1 | 4 | -4.063001 |
| LP2-40 | 231 | 32 | 1 | 3 | -4.007789 |
| LP2-41 | 273 | 30 | -1 | 6 | -4.249645 |
| LP2-42 | 272 | 31 | -1 | 5 | -4.250808 |
| LP2-43 | 274 | 30 | -1 | 2 | -4.283470 |
| LP2-44 | 273 | 32 | 1 | 15 | -4.248809 |
| LP2-45 | 270 | 32 | -1 | 17 | -4.226142 |
| LP2-46 | 270 | 32 | -1 | 9 | -4.225147 |
| LP2-47 | 274 | 32 | 1 | 11 | -4.306360 |
| LP2-48 | 271 | 32 | -1 | 23 | -4.208994 |
| LP2-52 | 263 | 32 | -1 | 2 | -4.216905 |
| LP2-54 | 232 | 32 | 1 | 22 | -3.985976 |
| LP2-00_02 | 729 | 32 | -1 | 24 | -5.394302 |
| LP2-03_07 | 1145 | 32 | -1 | 21 | -5.661851 |
| LP2-08_14 | 1729 | 30 | 1 | 19 | -5.935204 |
| LP2-15_22 | 1903 | 32 | -1 | 14 | -5.975291 |
| LP2-23_26 | 1021 | 32 | 1 | 21 | -5.603544 |
| LP2-27_32 | 1433 | 32 | 1 | 14 | -5.796041 |
| LP2-33_39 | 1680 | 32 | -1 | 14 | -5.939370 |
| LP2-40_53 | 3008 | 31 | 1 | 23 | -6.214282 |
| LP2-54_55 | 308 | 30 | 1 | 24 | -4.384546 |
| LP2-40_55 | 3316 | 31 | 1 | 23 | -6.246616 |

## Evidence

- [Original frozen report](../../reports/attack_phase24_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase24_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase24_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [general_feedback_plan.json](../../experiments/general_feedback_plan.json), [general_feedback_unknown_plan.json](../../experiments/general_feedback_unknown_plan.json), [phase24_summary.json](../../results/phase24_summary.json), [phase24_complete.json](../../checkpoints/phase24_complete.json).

[English candidate appendix](phase24_candidates.md).
