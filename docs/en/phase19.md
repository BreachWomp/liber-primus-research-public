# Phase 19: Long keys with page phases and a boundary ambiguity

**No new decryption confirmed.** Historical report date: 2026-10-21T15:29:02.227402+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E054 applies nominal lengths 17–32 with independent page phases and page-reset
language context. F-free initialization fragments cannot cross pages. Six new
windows at 6000:6729 and 8000:11316 in Emerson X–XII use keys 17/23/31,
random phases, and Bernoulli F-copy probabilities 0.25/0.50/0.75. Six earlier
E052 inputs are retained as regressions. **10/12 controls are exact.**
The fresh short length-17 case recovers 728/729; the fresh short length-31
case only 30/729. The remaining fresh short case, all three fresh long cases,
and six regressions are exact. One diagnostic null scores -5.555361.

E055 is an explicit known-key diagnostic registered after failure. With the
true key, the length-17 case still selects 728/729: wrong score -2.19317037
exceeds truth -2.19370452 by 0.00053415. The length-31 oracle is exact at
-2.32779446, showing a search failure in its blind run. Neither oracle is
counted as a decryption.

There is also a genuine ambiguity in the tested model. At a nonfirst page
starting with ciphertext F=0, normal decryption at phase p emits K[p] and
advances to p+1. Copying F at phase p+1 emits zero and reaches the same cursor.
The remaining text is identical and both recipes re-encrypt to the same
ciphertext. Two such pairs are saved and independently checked. A language
score can rank the alternatives but cannot remove algebraic ambiguity.
This is a property of this model, not proof of the actual LP cipher.

**No unknown pages are attacked with this failed variant.** **114 tests passed.**
Checks cover 13,728 pool states, 1,172 full-text states, 416 fragment maxima,
thirteen conditional full-text maxima, two oracle maxima, and both ambiguity
pairs. Fourteen tasks use 395.494 seconds within 1,200; sampled peak 127.3 MiB
against 768. The next proposal separates continuous language context from
the still-unresolved short-key initialization problem.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Chapter | Key | Correct runes | Text/key/mask/phases |
|---|---|---:|---:|---|
| New 0 | X | 17 | 728/729 | failed |
| New 1 | XI | 23 | 729/729 | exact |
| New 2 | XII | 31 | 30/729 | failed |
| New 3 | X | 17 | 3316/3316 | exact |
| New 4 | XI | 23 | 3316/3316 | exact |
| New 5 | XII | 31 | 3316/3316 | exact |
| Regression 0 | X | 17 | 1200/1200 | exact |
| Regression 1 | XI | 23 | 1200/1200 | exact |
| Regression 2 | XII | 31 | 1200/1200 | exact |
| Regression 3 | X | 17 | 3316/3316 | exact |
| Regression 4 | XI | 23 | 1200/1200 | exact |
| Regression 5 | XII | 31 | 1200/1200 | exact |

| Control | Oracle: correct runes | True score | Oracle-Score | Oracle minus true |
|---|---:|---:|---:|---:|
| fresh 0 | 728/729 | -2.19370452 | -2.19317037 | 0.00053415 |
| fresh 2 | 729/729 | -2.32779446 | -2.32779446 | 0.00000000 |

## Evidence

- [Original frozen report](../../reports/attack_phase19_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase19_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase19_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [long_phase_plan.json](../../experiments/long_phase_plan.json), [long_phase_diagnostic_plan.json](../../experiments/long_phase_diagnostic_plan.json), [phase19_summary.json](../../results/phase19_summary.json), [phase19_complete.json](../../checkpoints/phase19_complete.json).
