# Phase 4: External language training and longer autokey seeds

**No new decryption confirmed.** Historical report date: 2026-10-19T12:37:30.387846+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E016 trains on eleven pinned Emerson essays, excluding Self-Reliance because
it was used as a running-key hypothesis: 265,129 runes in 393 paragraphs.
No LP text is training data. Ligatures, combining accents, ASCII words, QU→CW,
remaining Q→C, and greedy within-word GP encoding are explicitly handled;
non-Latin letters are inventoried. Paragraph boundaries are not crossed.
Fixed order-three and order-four models (alpha=0.5, strength=5) recover
DIVINITY, CIRCUMFERENCE, and LP2-56 with exact F interruptions. The latter
uses the sole interruption at zero-based offset 56. Mutation comparisons favor
truth in 1,542/1,600 and 1,563/1,600 cases; these are correlated diagnostics on
previously seen controls, not blind validation.

E017 searches all 55 unknown rune pages for plaintext-autokey lengths 4–12,
four sign combinations, and none/all F. Cyclic trigram factors use a beam of
512 paths, every cyclic cut, and sixteen candidates per cut rescored with the
fourgram model. This is a bounded heuristic, not enumeration of 29^12 keys.
All six synthetic controls (lengths 4, 8, 12; seed 3301017) are exact. They do
not validate arbitrary interruption patterns. LP2-49 is selected at -3.303249;
3/19 fully optimized matched nulls reach its score: raw p=0.20, adjusted 1.

E018 repeats the 381-word-cycle and three-number-stream selective-F search
with the improved score. Its full-catalog controls are 3/3 exact. At this
historical checkpoint only **35/55 pages are complete**; remaining pages and
null calibration are pending. The phase ended at its budget, not at a negative
conclusion about the entire family. Phase 5 completes this work.

**61 tests passed; 306 candidate records were independently checked.**
Successful experiment time was 878.050 seconds. A partially processed group
LP2-35–39 was terminated and logged; accounting including termination reserve
was 891.052 seconds against 900. Completed fingerprints remain reusable;
the incomplete group must be rerun. No background task remained.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
EANOFEREWROWDSTTOGAUOPANSGOSPLUISAFFELETAIDSLOWNFRALRIDSPASSYEBTWOF
```

## Evidence

- [Original frozen report](../../reports/attack_phase4_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase4_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase4_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [emerson_manifest.json](../../sources/emerson_manifest.json), [phase4_budget.json](../../checkpoints/phase4_budget.json), [phase4_summary.json](../../results/phase4_summary.json), [phase4_complete.json](../../checkpoints/phase4_complete.json).
