# Phase 18: Repaired initialization and direct section attacks

**No new decryption confirmed.** Historical report date: 2026-10-21T10:42:40.560060+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E052 pools twelve F-free fragments (16–256 runes), using sixteen starts per
period/sign: three fixed phase rules plus thirteen seeded random vectors.
Up to twenty unigram alternations are followed by bigram/fourgram refinement.
Twenty diverse full-text starts then receive exact conditional F-schedule
optimization and up to three key/schedule rounds. Nominal lengths remain
17–32. Pool scoring charges free fragment phases; final selection uses the
full-text score. No true key, mask, or length is supplied.

All six controls are exact: three fresh 1,200-rune windows at offsets
4000:5200 in Emerson X–XII with lengths 17/23/31, and three unchanged E049
regressions of 3,316/1,200/1,200 runes. The old XII case improves from 59/1,200
and 78/1,200 to 1,200/1,200 with the correct key and schedule. Its exact key
appears only during full-text refinement, not in the saved pool states.
Training remains I and III–IX; controls copy every second plaintext F and
do not establish sensitivity to every interruption distribution or shorter
512–1,199-rune inputs. One matched optimized control null scores -5.842628.

E053 then attacks nine existing groups of at least 512 runes, covering all
55 unknown rune pages. LP2-54/55 occur within LP2-40_55; LP2-50 stays an empty
rune span. Group boundaries are hypotheses. LP2-00_02 is selected at -5.629978
with primitive key length 29. Eleven of nineteen full matched-null searches
reach it: raw p=0.60, Bonferroni9=1. Nulls preserve page counts, endpoints,
and adjacent matches and rerun every internal choice. With nineteen nulls,
the minimum possible nine-group-adjusted p-value is 0.45.

**111 tests passed.** Separate checks cover 36,960 pool states, 3,266 full-text
states, 1,120 enumerated fragment-phase maxima, and 35 full-text Viterbi maxima.
Thirty-five tasks take 494.129 seconds. E052/E053 budgets are 1,260/1,200 seconds,
maximum 180 per task, one worker. Sampled peak memory is 117.8 MiB against
768 MiB, sampled every 250 ms and not a guarantee of instantaneous peak usage.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Test | Chapter | Key length | Runes | Text, key, sign, F mask |
|---|---|---:|---:|---|
| Fresh | X | 17 | 1200 | exact |
| Fresh | XI | 23 | 1200 | exact |
| Fresh | XII | 31 | 1200 | exact |
| Regression | X | 17 | 3316 | exact |
| Regression | XI | 23 | 1200 | exact |
| Regression | XII | 31 | 1200 | exact |

| Section | Runes | Best primitive key length | Score |
|---|---:|---:|---:|
| LP2-00_02 | 729 | 29 | -5.629978 |
| LP2-03_07 | 1145 | 32 | -5.795490 |
| LP2-08_14 | 1729 | 26 | -6.046129 |
| LP2-15_22 | 1903 | 31 | -6.041130 |
| LP2-23_26 | 1021 | 30 | -5.811430 |
| LP2-27_32 | 1433 | 31 | -5.933181 |
| LP2-33_39 | 1680 | 32 | -6.001530 |
| LP2-40_53 | 3008 | 27 | -6.186528 |
| LP2-40_55 | 3316 | 31 | -6.199601 |

## Evidence

- [Original frozen report](../../reports/attack_phase18_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase18_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase18_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [fragment_initialization_plan.json](../../experiments/fragment_initialization_plan.json), [fragment_initialization_unknown_plan.json](../../experiments/fragment_initialization_unknown_plan.json), [phase18_summary.json](../../results/phase18_summary.json), [phase18_complete.json](../../checkpoints/phase18_complete.json).
