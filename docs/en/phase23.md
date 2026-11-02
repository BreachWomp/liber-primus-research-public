# Phase 23: Continuous autokey across sections

**No new decryption confirmed.** Historical report date: 2026-10-23T11:03:38.159082+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E064 keeps the E062 solver byte-identical: lengths 4–32, four signs, both
initializers, and unchanged refinement. The new application is longer text
with no reset of key, plaintext feedback, or language context across pages.
Four fresh 3,316-rune controls use keys 13/23/31/32 and all four sign pairs,
with LP2-40_55 page lengths including an empty numeric span. All four recover
text, key, and sign exactly. Twelve earlier shorter controls are reused via
source/code/output/validation hashes, not searched again. Source chapters are
previously seen. A fully optimized per-page matched control null scores
-6.248616 and receives no p-value.

E065 attacks all ten established section hypotheses, 308–3,316 runes, covering
all 55 unknown rune pages including those too short individually in phase 22.
Alternative overlapping LP2-40_53,54_55,40_55 groupings remain hypotheses.
LP2-50's preserved empty span does not decrypt its numbers. LP2-54_55 wins
at -4.471883 with initial key length 31. Fourteen of nineteen fully optimized
nulls reach it: raw p=0.75, Bonferroni10=1. Nulls preserve each page's counts,
endpoints, and adjacent matches. The smallest possible corrected value with
nineteen draws is 0.50, so this is only a coarse false-positive screen.

**126 tests passed.** Separate validation reconstructs source windows, scores,
conditional coordinate maxima, and re-encryptions. A rolling key queue is
checked across every page boundary and must remain unchanged on empty pages.
Nulls, seeds, selection rules, and hashes are reproduced. Thirty-four new tasks
use 657.460 seconds within 3,000; maximum 180 each, one worker, sampled peak
104.1 MiB against 768. The unchanged solver and all historical records remain.
The next proposal is general nonzero feedback multipliers at delays 4–32,
subject to an independently checked bounded family-selection stage.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Neue Control | Runes | Seed length | Plaintext/key/sign |
|---|---:|---:|---|
| 0 | 3316 | 13 | exact |
| 1 | 3316 | 23 | exact |
| 2 | 3316 | 31 | exact |
| 3 | 3316 | 32 | exact |

| Group | Runes | Recovered seed length | Score |
|---|---:|---:|---:|
| LP2-00_02 | 729 | 32 | -5.378248 |
| LP2-03_07 | 1145 | 29 | -5.701465 |
| LP2-08_14 | 1729 | 31 | -5.960524 |
| LP2-15_22 | 1903 | 30 | -6.014723 |
| LP2-23_26 | 1021 | 30 | -5.669823 |
| LP2-27_32 | 1433 | 32 | -5.823195 |
| LP2-33_39 | 1680 | 31 | -5.906238 |
| LP2-40_53 | 3008 | 32 | -6.244209 |
| LP2-54_55 | 308 | 31 | -4.471883 |
| LP2-40_55 | 3316 | 32 | -6.261514 |

## Evidence

- [Original frozen report](../../reports/attack_phase23_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase23_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase23_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [autokey_section_plan.json](../../experiments/autokey_section_plan.json), [autokey_section_unknown_plan.json](../../experiments/autokey_section_unknown_plan.json), [phase23_summary.json](../../results/phase23_summary.json), [phase23_complete.json](../../checkpoints/phase23_complete.json).
