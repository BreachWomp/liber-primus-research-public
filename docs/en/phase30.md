# Phase 30: General substitution on longer pages

**No new decryption confirmed.** Historical report date: 2026-11-02T16:40:59.828205+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E083 keeps the phase-29 model and optimizer unchanged and tests a separate
scope of at least 200 runes. Twelve other windows use four distinct paragraphs
per excluded Emerson chapter X/XI/XII, target prefixes 200/300/500/729 with the
last word kept whole. Actual lengths are 204,202,200,302,306,300,502,501,502,
729,730,730. All twelve plaintexts and mappings of observed symbols are exact.
Unobserved symbols remain unidentifiable. Keys and search seeds are fresh and
fixed in advance; texts are disjoint from fitting but historically seen.
Three fully optimized control nulls are diagnostics, not significance tests.
The earlier short-text counterexample remains unchanged.

After separate validation, E084 tests 46 unknown pages of at least 200 runes.
LP2-06/14/15/22/32/49/51/53/55 are shorter; LP2-50 is numeric. All exclusions
retain original content and reasons. Original lexical endpoints agree with
E026; all 56 research-page source anchors and ten source-file hashes are
checked. The search uses at most 24 starts, forty complete 406-swap character
sweeps, and forty BOS/EOS-word sweeps, without new tuning.

LP2-02 wins at **-7.593870**. Selection and 46 output hashes are frozen before
nineteen independent nulls. These preserve endpoints, counts, word boundaries,
and adjacent matches, with at most 100,000 rejection proposals. Every null
uses the full initializer and optimizer with the same page-specific seed.
**15/19** reach the observed score: raw p=0.80, Bonferroni46=1. Even the smallest
possible corrected value is 1. This is not evidence of plaintext recovery.

Control validation checks 257 scores, 99,470 final-neighbor scores, and 245
re-encryptions. Unknown/null validation checks 1,326 scores, 538,356 final
neighbors, and 1,326 re-encryptions. Language events are independently recounted
from sources, with shared tokenization; full optimization trajectories are not
separately implemented. This heuristic does not exhaust 29! mappings or
validate short texts, other languages, or other boundary conventions.

An initial start fails **before registry/search** because of a wrong benchmark
reference. Correcting it to the existing phase-29 validation changes no cipher
parameters; the original error log and separate retry log remain.
**142 tests passed; 80 completed tasks; 243.626 experiment seconds.** Monitored
process time including the start error is 295.176 seconds within 1,800, peak
170.0 MiB against 768, one worker.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Actual runes | Outcome |
|---|---:|---|
| 0 | 204 | exact |
| 1 | 202 | exact |
| 2 | 200 | exact |
| 3 | 302 | exact |
| 4 | 306 | exact |
| 5 | 300 | exact |
| 6 | 502 | exact |
| 7 | 501 | exact |
| 8 | 502 | exact |
| 9 | 729 | exact |
| 10 | 730 | exact |
| 11 | 730 | exact |

| Page | Runes | Highest score |
|---|---:|---:|
| LP2-00 | 262 | -8.374165 |
| LP2-01 | 266 | -8.329508 |
| LP2-02 | 201 | -7.593870 |
| LP2-03 | 217 | -7.937095 |
| LP2-04 | 261 | -8.534356 |
| LP2-05 | 263 | -8.172128 |
| LP2-07 | 208 | -7.843328 |
| LP2-08 | 255 | -8.085536 |
| LP2-09 | 268 | -8.184199 |
| LP2-10 | 263 | -8.628011 |
| LP2-11 | 273 | -8.240970 |
| LP2-12 | 261 | -8.629749 |
| LP2-13 | 272 | -8.576536 |
| LP2-16 | 267 | -8.348967 |
| LP2-17 | 273 | -8.776102 |
| LP2-18 | 260 | -8.601251 |
| LP2-19 | 271 | -8.399239 |
| LP2-20 | 269 | -8.585996 |
| LP2-21 | 273 | -8.324868 |
| LP2-23 | 213 | -8.193999 |
| LP2-24 | 270 | -8.622101 |
| LP2-25 | 273 | -8.490720 |
| LP2-26 | 265 | -8.394674 |
| LP2-27 | 234 | -8.006875 |
| LP2-28 | 269 | -8.391627 |
| LP2-29 | 277 | -8.788314 |
| LP2-30 | 263 | -8.376002 |
| LP2-31 | 269 | -8.653233 |
| LP2-33 | 214 | -8.263463 |
| LP2-34 | 261 | -8.394862 |
| LP2-35 | 271 | -8.184933 |
| LP2-36 | 238 | -8.037089 |
| LP2-37 | 228 | -8.298782 |
| LP2-38 | 228 | -7.946292 |
| LP2-39 | 240 | -8.174641 |
| LP2-40 | 231 | -8.290054 |
| LP2-41 | 273 | -8.514098 |
| LP2-42 | 272 | -8.350804 |
| LP2-43 | 274 | -8.094489 |
| LP2-44 | 273 | -8.243901 |
| LP2-45 | 270 | -8.432947 |
| LP2-46 | 270 | -8.649761 |
| LP2-47 | 274 | -8.378877 |
| LP2-48 | 271 | -8.568998 |
| LP2-52 | 263 | -8.445979 |
| LP2-54 | 232 | -8.313762 |

## Evidence

- [Original frozen report](../../reports/attack_phase30_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase30_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase30_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [long_substitution_controls_plan.json](../../experiments/long_substitution_controls_plan.json), [long_substitution_unknown_plan.json](../../experiments/long_substitution_unknown_plan.json), [phase30_summary.json](../../results/phase30_summary.json).

[English candidate appendix](phase30_candidates.md).
