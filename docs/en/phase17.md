# Phase 17: Long keys expose an initialization failure

**No new decryption confirmed.** Historical report date: 2026-10-21T10:24:33.561076+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E049 extends nominal periodic keys to 17–32 runes, with continuous state and
selective F copies. Input length is 512–4,096; maximum DP state count 256.
Starts come from full or end windows and three long F-free spans; twelve
deduplicated keys receive up to three refinement rounds. Fixed-key schedule
optimization is exact, global key search is not.

| Control chapter | Key length | Runes | Recovery |
|---|---:|---:|---|
| X | 17 | 3316 | Exact |
| XI | 23 | 1200 | Exact |
| XII | 31 | 1200 | 59/1200 correct |

E050 diagnoses the failed length-31 case. Truth scores -2.309824 versus the
found -5.810931, a 3.501106 advantage. The true key is absent from starts and
final keys; all twelve starts came from one 65-rune F-free span. Two explicit
oracle checks succeed: known key recovers the F mask; known length and the
correct mask on the first 1,024 runes recover the key and prefix. These use
solution information and are not independent decryptions. They point to a
search failure rather than an objective that prefers the wrong text.

E051 is a separately registered adaptive repair: pool twelve F-free fragments
of at least sixteen runes, allow separate phases, and use two joint refinement
rounds before the existing full-text optimizer. Parameters were chosen after
seeing E049's failure. Twelve fragments total 512 runes; the repair still
recovers only 78/1,200, score -5.870172. One fully optimized matched null scores
-5.770010; no p-value is assigned. **No unknown-page attack is authorized by
these failed controls.**

**108 tests passed.** Validation covers 342 candidates, 72 starts/trajectories,
72 fragment states, six conditional maxima, original windows, keys, and both
nulls. Three experiments take 162.750 seconds within 900, maximum 180 each.
Earlier failures remain unchanged; future repair must also pass fresh cases.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Chapter | Key length | Runes | Text, key, and F mask |
|---|---:|---:|---|
| X | 17 | 3316 | exact |
| XI | 23 | 1200 | exact |
| XII | 31 | 1200 | failed |

## Evidence

- [Original frozen report](../../reports/attack_phase17_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase17_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase17_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [long_key_plan.json](../../experiments/long_key_plan.json), [long_key_diagnostic_plan.json](../../experiments/long_key_diagnostic_plan.json), [pooled_long_key_plan.json](../../experiments/pooled_long_key_plan.json), [phase17_summary.json](../../results/phase17_summary.json), [phase17_complete.json](../../checkpoints/phase17_complete.json).
