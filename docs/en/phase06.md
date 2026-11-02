# Phase 6: Image layout, reading routes, and numeric transcriptions

**No new decryption confirmed.** Historical report date: 2026-10-19T17:40:46.443777+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

Seven page images were inspected for line count, order, and endpoints:
LP2-00,49,50,51,55,56,57. This was not a full independent glyph transcription.
Pinned images, approximate pixel regions, timestamps, and hashes are retained.
Unequal line lengths are preserved rather than padded into invented columns.

E021 tests eight bijective reading routes on preselected LP2-00,49,51,55:
top/bottom line order combined with left/right or alternating within-line
directions. Routing precedes decryption. Each route searches 812 affine maps,
the two known key cycles with all phases, and primes/p−1/totients at starts
0–255 with four signs and exact F subsets. The route search is bounded, not
an arbitrary transposition attack. Eight rerouted LP2-56 controls plus LP2-57
are exact. Selected LP2-49 uses `top_snake_right`, score -5.304835; 13/19 fully
searched nulls match or exceed it: raw p=0.70, conservative Bonferroni55=1.
The four pages were partly selected using earlier scores, so they are not a
fresh random sample. Nulls preserve counts and stored-order adjacent matches.

E022 compares the **256 numeric cells** on LP2-49/50/51. The prior-art base60
alphabet is `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx`;
pair value is 60 times the first index plus the second. All interpreted values
lie in 0–255, which does not establish a file type or encryption.

| Page, row, column (one-based) | relikd / iddqd / scream314 | Values |
|---|---|---|
| LP2-49,6,6 | 1L / 1l / 1l | 81 / 107 / 107 |
| LP2-49,7,3 | 0L / 0l / 0l | 21 / 47 / 47 |
| LP2-50,11,6 | 0l / 0I / 0I | 47 / 18 / 18 |
| LP2-50,12,5 | 2s / 2S / 2S | 174 / 148 / 148 |
| LP2-51,8,7 | 3i / 3I / 3I | 224 / 198 / 198 |

Nine entries in scream314's decimal table also disagree with conversion of
its own base60 tokens. These conflicts remain unresolved in this phase;
case is not silently normalized. All variants are retained. **67 tests passed;
39 route candidates were independently inverted and rescored.** Twenty-five
successful tasks used 272.814 seconds within a 900-second budget.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
OEFCNGLIAMAGMBAEDUSTHYWATHWIPTALEAUOIACHNGFAEYTEAPIACDMDCRNGPOREORNGBEENDXELEMCSF
```

## Evidence

- [Original frozen report](../../reports/attack_phase6_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase6_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase6_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [layout_images_manifest.json](../../sources/layout_images_manifest.json), [layout_audit.json](../../sources/layout_audit.json), [E022-numeric-source-audit-7f284cff4638.json](../../results/E022-numeric-source-audit-7f284cff4638.json), [phase6_complete.json](../../checkpoints/phase6_complete.json), [phase6_summary.json](../../results/phase6_summary.json).
